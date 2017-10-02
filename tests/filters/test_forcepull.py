#encoding: utf-8

from hollowman.filters.forcepull import ForcePullFilter
from unittest import TestCase
from tests import RequestStub
from hollowman.filters import Context

from marathon.models.app import MarathonApp
import mock
from tests.utils import with_json_fixture


class ForcePullTest(TestCase):

    def setUp(self):
        self.ctx = Context(marathon_client=None, request=None)
        self.filter = ForcePullFilter()

    def test_simple_app(self):
        data = {
            "id": "/foo/bar",
            "container":{
                "docker":{
                    "image": "alpine:3.4"
                }
            }
        }
        with mock.patch.object(self, "ctx") as ctx_mock:
            request = RequestStub(path="/v2/apps//app/foo", data=data, method="PUT")
            ctx_mock.marathon_client.get_app.return_value = MarathonApp(**data)

            self.ctx.request = request
            modified_request = self.filter.run(self.ctx)
            self.assertEqual(
                True,
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

        with mock.patch.object(self, "ctx") as ctx_mock:
            request = RequestStub(path="/v2/apps//app/foo", data=data, method="PUT")
            ctx_mock.marathon_client.get_app.return_value = MarathonApp(**data)

            self.ctx.request = request
            modified_request = self.filter.run(self.ctx)
            self.assertTrue(
                modified_request.get_json()['container']['docker']['forcePullImage']
            )
            self.assertEqual("data", modified_request.get_json()['container']['volumes'][0]['containerPath'])
            self.assertTrue("type" in modified_request.get_json()['container'])

    def test_app_creation(self):
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

        with mock.patch.object(self, "ctx") as ctx_mock:
            request = RequestStub(path="/v2/apps/", data=data, method="POST")
            # if the app does not exist, get_app() returns an empty marathon.models.app.MarathonApp()
            ctx_mock.marathon_client.get_app.return_value = MarathonApp()

            self.ctx.request = request
            modified_request = self.filter.run(self.ctx)
            self.assertTrue(
                modified_request.get_json()['container']['docker']['forcePullImage']
            )
            self.assertEqual("data", modified_request.get_json()['container']['volumes'][0]['containerPath'])
            self.assertTrue("type" in modified_request.get_json()['container'])

    @with_json_fixture("single_full_app.json")
    def test_app_exists_forcepull_not_checked(self, single_full_app_fixture):
        original_app = MarathonApp.from_json(single_full_app_fixture)
        request_app = MarathonApp.from_json(single_full_app_fixture)
        request_app.container.docker.force_pull_image = False

        modified_request_app = self.filter.write(user=None, request_app=request_app, app=original_app)
        self.assertTrue(modified_request_app.container.docker.force_pull_image, True)

    @with_json_fixture("single_full_app.json")
    def test_creating_app_forcepull_not_checked(self, single_full_app_fixture):
        original_app = MarathonApp()
        request_app = MarathonApp.from_json(single_full_app_fixture)
        request_app.container.docker.force_pull_image = True

        modified_request_app = self.filter.write(user=None, request_app=request_app, app=original_app)
        self.assertTrue(modified_request_app.container.docker.force_pull_image, True)

    @with_json_fixture("single_full_app.json")
    def test_empty_request_app(self, single_full_app_fixture):
        """
        Isso acontece quando é um request de restart, por exemplo, onde o body do request é vazio.
        """
        original_app = MarathonApp.from_json(single_full_app_fixture)
        request_app = MarathonApp()

        modified_request_app = self.filter.write(user=None, request_app=request_app, app=original_app)
        self.assertTrue(request_app is modified_request_app)
