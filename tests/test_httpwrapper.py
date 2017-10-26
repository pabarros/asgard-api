
from unittest import TestCase
from unittest.mock import Mock

from hollowman.app import application
from hollowman.http_wrappers.request import Request

class HTTPWrapperTest(TestCase):

    def test_it_recognizes_group_requests(self):
        with application.test_request_context('/v2/groups/',
                                              method='GET', data=b'') as ctx:
            request_parser = Request(ctx.request)
            self.assertTrue(request_parser.is_group_request())
            self.assertFalse(request_parser.is_app_request())

        with application.test_request_context('/v2/groups/xablau/Xena',
                                              method='PUT', data=b'') as ctx:
            request_parser = Request(ctx.request)
            self.assertTrue(request_parser.is_group_request())
            self.assertFalse(request_parser.is_app_request())

        with application.test_request_context('/v2/groups/xablau',
                                              method='DELETE', data=b'') as ctx:
            request_parser = Request(ctx.request)
            self.assertTrue(request_parser.is_group_request())
            self.assertFalse(request_parser.is_app_request())

    def test_it_recognizes_apps_requests(self):
        with application.test_request_context('/v2/apps//foo',
                                              method='GET', data=b'') as ctx:
            request_parser = Request(ctx.request)
            self.assertTrue(request_parser.is_app_request())
            self.assertFalse(request_parser.is_group_request())

        with application.test_request_context('/v2/apps/',
                                              method='PUT', data=b'') as ctx:
            request_parser = Request(ctx.request)
            self.assertTrue(request_parser.is_app_request())
            self.assertFalse(request_parser.is_group_request())

        with application.test_request_context('/v2/apps//',
                                              method='DELETE', data=b'') as ctx:
            request_parser = Request(ctx.request)
            self.assertTrue(request_parser.is_app_request())
            self.assertFalse(request_parser.is_group_request())

    def test_it_parsers_marathon_app_path(self):
        expected_paths = {
            '/v2/apps/xablau': '/xablau',
            '/v2/apps//xablau': '/xablau',
            '/v2/apps/xablau/xena': '/xablau/xena',
            '/v2/apps////': None,
            '/v2/apps': None,
            '/v2/apps/': None,
            '/v2/apps/xablau/restart': '/xablau',
            '/v2/apps//xablau/restart': '/xablau',
            '/v2/apps/xablau/tasks': '/xablau',
            '/v2/apps//xablau/tasks': '/xablau',
            '/v2/apps/xablau/versions': '/xablau',
            '/v2/apps//xablau/versions': '/xablau'
        }

        for request_path, expected_marathon_path in expected_paths.items():
            # noinspection PyTypeChecker
            parser = Request(Mock(path=request_path))
            self.assertEqual(parser.app_id, expected_marathon_path)

    def test_it_raises_an_error_if_get_app_id_is_called_for_v2groups_path(self):
        with self.assertRaises(ValueError):
            Request(Mock(path='/v2/groups/xablau')).app_id
