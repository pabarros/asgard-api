#encoding: utf-8

from hollowman.filters.trim import TrimEnvVarsRequestFilter
from unittest import TestCase
from tests import RequestStub
import json


class TrimEnvvarsTest(TestCase):

    def setUp(self):
        self.filter = TrimEnvVarsRequestFilter()

    def test_absent_env_key(self):
        data_ = {
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
            },
        }
        request = RequestStub(data=data_)
        modified_request = self.filter.run(request)
        self.assertDictEqual(data_, modified_request.get_json())

    def test_empty_env_vars(self):
        data_ = {
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
            },
            "env": {}
        }
        request = RequestStub(data=data_)
        modified_request = self.filter.run(request)
        self.assertDictEqual(data_, modified_request.get_json())

    def test_json_with_one_env_var(self):
        data_ = {
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
            },
            "env": {
                "MY_ENV": " abc "
            }
        }
        request = RequestStub(data=data_)
        modified_request = self.filter.run(request)
        self.assertEqual(modified_request.get_json()['env']['MY_ENV'], "abc")

    def test_json_with_multiple_env_vars(self):
        data_ = {
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
            },
            "env": {
                "MY_ENV": " abc ",
                "OTHER_ENV": " 10.0.0.1",
                "ANOTHER_ENV_WITH_SPACES": "  some spaces "
            }
        }
        request = RequestStub(data=data_)
        modified_request = self.filter.run(request)
        self.assertEqual(modified_request.get_json()['env']['MY_ENV'], "abc")
        self.assertEqual(modified_request.get_json()['env']['OTHER_ENV'], "10.0.0.1")
        self.assertEqual(modified_request.get_json()['env']['ANOTHER_ENV_WITH_SPACES'], "some spaces")
