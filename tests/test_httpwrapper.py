
from unittest import TestCase
from unittest.mock import Mock

from hollowman.app import application
from hollowman.http_wrappers.request import Request
from hollowman.http_wrappers.response import Response
from hollowman.http_wrappers.base import RequestResource

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
            '/v2/apps//xablau/versions': '/xablau',

            '/v2/queue//xablau/delay': '/xablau',
            '/v2/queue/xablau/delay': '/xablau'
        }

        for request_path, expected_marathon_path in expected_paths.items():
            # noinspection PyTypeChecker
            parser = Request(Mock(path=request_path))
            self.assertEqual(parser.object_id, expected_marathon_path)

    def test_it_parses_marathon_group_id(self):
        expected_paths = {
            '/v2/groups/xablau': '/xablau',
            '/v2/groups//xablau': '/xablau',
            '/v2/groups/xablau/xena': '/xablau/xena',
            '/v2/groups////': None,
            '/v2/groups': None,
            '/v2/groups/': None,
            '/v2/groups/versions': None,
            '/v2/groups/xablau/restart': '/xablau/restart',
            '/v2/groups//xablau/restart': '/xablau/restart',
            '/v2/groups/xablau/tasks': '/xablau/tasks',
            '/v2/groups//xablau/tasks': '/xablau/tasks',
            '/v2/groups/xablau/versions': '/xablau',
            '/v2/groups//xablau/versions': '/xablau'
        }

        for request_path, expected_marathon_path in expected_paths.items():
            # noinspection PyTypeChecker
            parser = Request(Mock(path=request_path))
            self.assertEqual(parser.object_id, expected_marathon_path)

    def test_it_parses_deployment_id(self):
        expected_paths = {
            '/v2/deployments/727ece1a-0496-4bc0-84a3-c3b69c49f8e6': '/727ece1a-0496-4bc0-84a3-c3b69c49f8e6',
            '/v2/deployments//727ece1a-0496-4bc0-84a3-c3b69c49f8e6': '/727ece1a-0496-4bc0-84a3-c3b69c49f8e6',
            '/v2/deployments/': None,
            '/v2/deployments///': None,
        }

        for request_path, expected_marathon_path in expected_paths.items():
            # noinspection PyTypeChecker
            request_wrapper = Request(Mock(path=request_path))
            self.assertEqual(request_wrapper.object_id, expected_marathon_path)

    def test_it_parses_task_id(self):
        expected_paths = {
            '/v2/tasks': None,
            '/v2/tasks/': None,
            '/v2/tasks/delete': None,
        }

        for request_path, expected_marathon_path in expected_paths.items():
            # noinspection PyTypeChecker
            request_wrapper = Request(Mock(path=request_path))
            self.assertEqual(request_wrapper.object_id, expected_marathon_path)

    def test_is_delete(self):
        with application.test_request_context('/v2/apps/app0',
                                              method='DELETE', data=b'') as ctx:
            request_parser = Request(ctx.request)
            self.assertTrue(request_parser.is_delete())

    def test_is_post(self):
        with application.test_request_context('/v2/apps/',
                                              method='POST', data=b'') as ctx:
            request_parser = Request(ctx.request)
            self.assertTrue(request_parser.is_post())

    def test_is_queue_request(self):
        with application.test_request_context('/v2/queue/',
                                              method='GET') as ctx:
            request_parser = Request(ctx.request)
            self.assertTrue(request_parser.is_queue_request())

    def test_is_tasks_request(self):
        with application.test_request_context('/v2/tasks/',
                                              method='GET') as ctx:
            request_parser = Request(ctx.request)
            self.assertTrue(request_parser.is_tasks_request())

    def test_return_correct_request_resource(self):
        expected_request_resources = {
            '/v2/apps': RequestResource.APPS,
            '/v2/apps/': RequestResource.APPS,
            '/v2/groups': RequestResource.GROUPS,
            '/v2/groups/': RequestResource.GROUPS,
            '/v2/deployments': RequestResource.DEPLOYMENTS,
            '/v2/deployments/': RequestResource.DEPLOYMENTS,
            '/v2/tasks': RequestResource.TASKS,
            '/v2/tasks/': RequestResource.TASKS,
            '/v2/queue': RequestResource.QUEUE,
            '/v2/queue/': RequestResource.QUEUE,
        }

        for request_path, expected_request_resource in expected_request_resources.items():
            # noinspection PyTypeChecker
            request_mock = Mock(path=request_path)
            request_wrapper = Request(request_mock)
            response_wrapper = Response(request_mock, Mock())
            self.assertEqual(request_wrapper.request_resource, expected_request_resource)
            self.assertEqual(response_wrapper.request_resource, expected_request_resource)

