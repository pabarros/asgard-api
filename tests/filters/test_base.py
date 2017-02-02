#encoding: utf-8

from hollowman.filters import BaseFilter
from hollowman.filters.request import _ctx
import unittest


class BaseFilterTest(unittest.TestCase):

    def setUp(self):
        self.filter = BaseFilter(_ctx)

    def test_is_request_on_app(self):
        self.assertTrue(self.filter.is_request_on_app("/v2/apps//app/foo"))
        self.assertFalse(self.filter.is_request_on_app("/v2/apps/"))
        self.assertTrue(self.filter.is_request_on_app("/v2/apps//app/foo/versions"))
        self.assertFalse(self.filter.is_request_on_app("/v2/apps"))
        self.assertFalse(self.filter.is_request_on_app("/v2/groups"))

    def test_get_app_id(self):
        self.assertEqual('/foo', self.filter.get_app_id('/v2/apps//foo'))
        self.assertEqual('/foo/taz/bar', self.filter.get_app_id('/v2/apps//foo/taz/bar'))
        self.assertEqual('/foo/taz', self.filter.get_app_id('/v2/apps//foo/taz/restart'))
        self.assertEqual('/foo/taz', self.filter.get_app_id('/v2/apps//foo/taz/restart/'))
        self.assertEqual('/foo/taz-restart', self.filter.get_app_id('/v2/apps//foo/taz-restart/versions/version-id'))

        self.assertEqual('/foo/taz', self.filter.get_app_id('/v2/apps//foo/taz/tasks'))
        self.assertEqual('/foo/taz', self.filter.get_app_id('/v2/apps//foo/taz/tasks/'))
        self.assertEqual('/foo/taz', self.filter.get_app_id('/v2/apps//foo/taz/tasks/task-id'))
        self.assertEqual('/foo/taz-tasks', self.filter.get_app_id('/v2/apps//foo/taz-tasks/versions/version-id'))
        
        self.assertEqual('/foo/taz', self.filter.get_app_id('/v2/apps//foo/taz/versions'))
        self.assertEqual('/foo/taz', self.filter.get_app_id('/v2/apps//foo/taz/versions/'))
        self.assertEqual('/foo/taz', self.filter.get_app_id('/v2/apps//foo/taz/versions/version-id'))
        self.assertEqual('/foo/taz-versions', self.filter.get_app_id('/v2/apps//foo/taz-versions/versions/version-id'))


    def test_is_docker_app(self):
        data_ = {
            "id": "/",
            "apps": [],
            "groups": []
        }
        self.assertFalse(self.filter.is_docker_app(data_))
        data_ = {
            "id": "/foo",
            "container": {
                "docker": {
                    "image": "alpine:3.4"
                }
            }
        }
        self.assertTrue(self.filter.is_docker_app(data_))

    def test_get_apps_from_groups(self):
        data_ = {"id": "/"}
        self.assertEqual([], self.filter.get_apps_from_group(data_))

        data_ = {
            "id": "/",
            "apps": [
                {},
                {},
                {},
            ]
        }
        self.assertEqual([{}, {}, {}], self.filter.get_apps_from_group(data_))

    def test_is_group(self):
        data_ = {
            "id": "/",
            "groups": [
                {
                  "id": "/bla"
                },
                {
                    "id": "/foo"
                }
            ]
        }
        self.assertTrue(self.filter.is_group(data_))
        data_ = {
            "id": "/abc",
            "container": {
                "docker": {
                }
            }
        }
        self.assertFalse(self.filter.is_group(data_))

    def test_is_single_app(self):
        data_ = {
            "id": "/daltonmatos/sleep2",
            "cmd": "sleep 40000",
            "cpus": 1,
            "mem": 128,
            "disk": 0,
            "instances": 0,
            "container": {
                  "type": "DOCKER",
                  "docker": {
                      "image": "alpine:3.4",
                      "network": "BRIDGE",
                  },
            }
        }
        self.assertTrue(self.filter.is_single_app(data_))
        data_ = {"id": "/foo", "apps": {}}
        self.assertFalse(self.filter.is_single_app(data_))
        data_ = {"id": "/foo", "groups": {}}
        self.assertFalse(self.filter.is_single_app(data_))

        data_ = [
            {"id": "/foo"},
            {"id": "/bar"}
        ]
        self.assertFalse(self.filter.is_single_app(data_))

    def test_is_multi_app(self):
        data_ = [
            {"id": "/foo"},
            {"id": "/bar"}
        ]
        self.assertTrue(self.filter.is_multi_app(data_))
