#encoding: utf-8

from hollowman.filters.forcepull import ForcePullFilter
from unittest import TestCase
from tests import RequestStub
import json
from hollowman.filters import Context
from hollowman.filters.request import _ctx


class ForcePullTest(TestCase):

    def setUp(self):
        self.filter = ForcePullFilter(_ctx)

    def test_simple_app(self):
        data = {"id": "/foo/bar"}
        request = RequestStub(data=data)
        modified_request = self.filter.run(request)
        self.assertEqual(
            True,
            modified_request.get_json()['container']['docker']['forcePullImage']
        )

    def test_simple_app_disable_pull(self):
        data = {
            "id": "/foo/bar",
            "labels": {
                "hollowman.disable_forcepull": "any_value"
            }
        }
        request = RequestStub(data=data)
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
        request = RequestStub(data=data)
        modified_request = self.filter.run(request)
        self.assertTrue(
            modified_request.get_json()['container']['docker']['forcePullImage']
        )
        self.assertEqual("data", modified_request.get_json()['container']['volumes']['containerPath'])
        self.assertTrue("type" in modified_request.get_json())
