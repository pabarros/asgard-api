from marathon import MarathonApp
from mock import Mock

from hollowman.filters.trim import TrimRequestFilter, TrimEnvvarsFilter
from unittest import TestCase
from tests import RequestStub
from hollowman.filters import Context


class TrimEnvvarsTest(TestCase):

    def setUp(self):
        self.ctx = Context(marathon_client=None, request=None)
        self.filter = TrimRequestFilter()

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
        self.ctx.request = request
        modified_request = self.filter.run(self.ctx)
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
        self.ctx.request = request
        modified_request = self.filter.run(self.ctx)
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
        self.ctx.request = request
        modified_request = self.filter.run(self.ctx)
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
        self.ctx.request = request
        modified_request = self.filter.run(self.ctx)
        self.assertEqual(modified_request.get_json()['env']['MY_ENV'], "abc")
        self.assertEqual(modified_request.get_json()['env']['OTHER_ENV'], "10.0.0.1")
        self.assertEqual(modified_request.get_json()['env']['ANOTHER_ENV_WITH_SPACES'], "some spaces")

    def test_json_with_multiple_env_vars_key_with_space(self):
        data_ = {
            "id": "/foo/bar",
            "cmd": "sleep 5000",
            "cpus": 1,
            "mem": 128,
            "disk": 0,
            "instances": 1,
            "container": {
            },
            "env": {
                "  MY_ENV  ": " abc ",
                " OTHER_ENV   ": " 10.0.0.1",
            }
        }
        request = RequestStub(data=data_)
        self.ctx.request = request
        modified_request = self.filter.run(self.ctx)
        self.assertFalse('  MY_ENV  ' in modified_request.get_json()['env'])
        self.assertFalse(' OTHER_ENV   ' in modified_request.get_json()['env'])

    def test_trim_all_labels(self):
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
            "labels": {
                "MY_LABEL ": " abc ",
                "  OTHER_LABEL  ": " 10.0.0.1 ",
            }
        }
        request = RequestStub(data=data_)
        self.ctx.request = request
        modified_request = self.filter.run(self.ctx)
        self.assertEqual(modified_request.get_json()['labels']['MY_LABEL'], "abc")
        self.assertEqual(modified_request.get_json()['labels']['OTHER_LABEL'], "10.0.0.1")
        self.assertFalse('MY_LABEL ' in modified_request.get_json()['labels'])
        self.assertFalse('  OTHER_LABEL  ' in modified_request.get_json()['labels'])


class TrimEnvvarsFilterTests(TestCase):
    def setUp(self):
        self.filter = TrimEnvvarsFilter()

    def test_it_trims_envvars_values(self):
        pass

    def test_it_trims_labels(self):
        app_dict = {
            "labels": {
                "Label": "xablau",
                "     MY_LABEL    ": "    abc   ",
                "    OTHER_LABEL     ": "    10.0.0.1    ",
            }
        }
        request_app = MarathonApp.from_json(app_dict)
        filtered_app = self.filter.write(Mock(), request_app, Mock())
        filtered_app = filtered_app.json_repr()

        self.assertDictEqual(filtered_app['labels'],
                             {
                                 "Label": "xablau",
                                 "MY_LABEL": "abc",
                                 "OTHER_LABEL": "10.0.0.1"
                             })

    def test_it_trims_envvars(self):
        app_dict = {
            "env": {
                "ENV": "xablau",
                "  MY_ENV  ": "    abc  ",
                "     OTHER_ENV   ": "    10.0.0.1     ",
            }
        }
        request_app = MarathonApp.from_json(app_dict)
        filtered_app = self.filter.write(Mock(), request_app, Mock())
        filtered_app = filtered_app.json_repr()

        self.assertDictEqual(filtered_app['env'],
                             {
                                 "ENV": "xablau",
                                 "MY_ENV": "abc",
                                 "OTHER_ENV": "10.0.0.1"
                             })

    def test_absent_env_and_labels_keys(self):
        app_dict = {
            "id": "/foo/bar",
            "cmd": "sleep 5000",
            "cpus": 1,
            "mem": 128,
            "disk": 0,
            "instances": 1
        }
        request_app = MarathonApp.from_json(app_dict)
        filtered_app = self.filter.write(Mock(), request_app, Mock())
        filtered_app = filtered_app.json_repr()

        self.assertEqual(filtered_app['env'], None)
        self.assertEqual(filtered_app['labels'], {})

    def test_empty_env(self):
        app_dict = {
            "env": {}
        }
        request_app = MarathonApp.from_json(app_dict)
        filtered_app = self.filter.write(Mock(), request_app, Mock())
        filtered_app = filtered_app.json_repr()

        self.assertDictEqual(filtered_app['env'], {})


    def test_empty_labels(self):
        app_dict = {
            "labels": {}
        }
        request_app = MarathonApp.from_json(app_dict)
        filtered_app = self.filter.write(Mock(), request_app, Mock())
        filtered_app = filtered_app.json_repr()

        self.assertDictEqual(filtered_app['labels'], {})
