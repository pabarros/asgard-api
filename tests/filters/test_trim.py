from marathon import MarathonApp
from mock import Mock

from hollowman.filters.trim import TrimRequestFilter
from unittest import TestCase

class TrimRequestFilterTest(TestCase):
    def setUp(self):
        self.filter = TrimRequestFilter()

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
        #filtered_app = filtered_app.json_repr()

        self.assertEqual(filtered_app.env, {})
        self.assertEqual(filtered_app.labels, {})

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
