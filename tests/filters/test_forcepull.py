#encoding: utf-8

from hollowman.filters.forcepull import ForcePullFilter
from unittest import TestCase
from tests import RequestStub
from hollowman.filters.request import _ctx

from marathon.models.app import MarathonApp
import mock

class ForcePullTest(TestCase):

    def setUp(self):
        self.filter = ForcePullFilter(_ctx)

    def test_simple_app(self):
        data = {
            "id": "/foo/bar",
            "container":{
                "docker":{
                    "image": "alpine:3.4"
                }
            }
        }
        with mock.patch.object(self.filter, "ctx") as ctx_mock:
            request = RequestStub(path="/v2/apps//app/foo", data=data, method="PUT")
            ctx_mock.marathon_client.get_app.return_value = MarathonApp(**data)

            modified_request = self.filter.run(request)
            self.assertEqual(
                True,
                modified_request.get_json()['container']['docker']['forcePullImage']
            )

    def test_simple_app_disable_pull(self):
        data = {
            "id": "/foo/bar",
            "container":{
                "docker":{
                    "image": "alpine:3.4"
                }
            },
            "labels": {
                "hollowman.disable_forcepull": "any_value"
            }
        }

        with mock.patch.object(self.filter, "ctx") as ctx_mock:
            request = RequestStub(path="/v2/apps//app/foo", data=data, method="PUT")
            ctx_mock.marathon_client.get_app.return_value = MarathonApp(**data)

            modified_request = self.filter.run(request)
            self.assertEqual(
                False,
                modified_request.get_json()['container']['docker']['forcePullImage']
            )

    def test_app_with_fields(self):
        data = {
            "id": "/foo/bar",
            "cmd": "sleep 5000",
            "cpus": 1,
            "mem": 128,
            "disk": 0,
            "instances": 1,
            "container": {
                "docker": {
                    "image": "alpine:3.4"
                },
                "volumes": [
                    {
                        "containerPath": "data",
                        "persistent": {
                            "size": 128
                        },
                        "mode": "RW"
                    }
                ],
                "type": "MESOS"
            }
        }

        with mock.patch.object(self.filter, "ctx") as ctx_mock:
            request = RequestStub(path="/v2/apps//app/foo", data=data, method="PUT")
            ctx_mock.marathon_client.get_app.return_value = MarathonApp(**data)

            modified_request = self.filter.run(request)
            self.assertTrue(
                modified_request.get_json()['container']['docker']['forcePullImage']
            )
            self.assertEqual("data", modified_request.get_json()['container']['volumes'][0]['containerPath'])
            self.assertTrue("type" in modified_request.get_json()['container'])
