import json
from unittest import TestCase
from unittest.mock import patch, Mock

from marathon import NotFoundError, MarathonApp
from responses import RequestsMock

from hollowman import conf
from hollowman.app import application
from hollowman.hollowman_flask import HollowmanRequest
from hollowman.parsers import RequestParser
from tests.utils import with_json_fixture, get_fixture


class RequestParserTests(TestCase):

    def test_it_recognizes_group_requests(self):
        with application.test_request_context('/v2/groups/',
                                              method='GET', data=b'') as ctx:
            request_parser = RequestParser(ctx.request)
            self.assertTrue(request_parser.is_group_request())
            self.assertFalse(request_parser.is_app_request())

        with application.test_request_context('/v2/groups/xablau/Xena',
                                              method='PUT', data=b'') as ctx:
            request_parser = RequestParser(ctx.request)
            self.assertTrue(request_parser.is_group_request())
            self.assertFalse(request_parser.is_app_request())

        with application.test_request_context('/v2/groups/xablau',
                                              method='DELETE', data=b'') as ctx:
            request_parser = RequestParser(ctx.request)
            self.assertTrue(request_parser.is_group_request())
            self.assertFalse(request_parser.is_app_request())

    def test_it_recognizes_apps_requests(self):
        with application.test_request_context('/v2/apps//foo',
                                              method='GET', data=b'') as ctx:
            request_parser = RequestParser(ctx.request)
            self.assertTrue(request_parser.is_app_request())
            self.assertFalse(request_parser.is_group_request())

        with application.test_request_context('/v2/apps/',
                                              method='PUT', data=b'') as ctx:
            request_parser = RequestParser(ctx.request)
            self.assertTrue(request_parser.is_app_request())
            self.assertFalse(request_parser.is_group_request())

        with application.test_request_context('/v2/apps//',
                                              method='DELETE', data=b'') as ctx:
            request_parser = RequestParser(ctx.request)
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
            parser = RequestParser(Mock(path=request_path))
            self.assertEqual(parser.app_id, expected_marathon_path)

    def test_it_raises_an_error_if_get_app_id_is_called_for_v2groups_path(self):
        with self.assertRaises(ValueError):
            RequestParser(Mock(path='/v2/groups/xablau')).app_id


class SplitTests(TestCase):
    # todo: debater nome request_app e app <- app fica ambíguo
    @with_json_fixture('single_full_app.json')
    def test_a_read_single_app_request_returns_a_single_marathonapp_if_app_exists(self, fixture):
        with application.test_request_context('/v2/apps//foo',
                                              method='GET', data=b'') as ctx:
            request_parser = RequestParser(ctx.request)

            with patch.object(request_parser, 'marathon_client') as client:
                client.get_app.return_value = MarathonApp.from_json(fixture)
                apps = list(request_parser.split())

            self.assertEqual(
                apps,
                [
                    (MarathonApp(), client.get_app.return_value)
                ])

    def test_a_read_single_app_request_returns_an_errorif_app_doesnt_exists(self):
        with application.test_request_context('/v2/apps//foo', method='GET') as ctx:
            request_parser = RequestParser(ctx.request)

            with patch.object(request_parser, 'marathon_client') as client:
                response_mock = Mock()
                response_mock.headers.get.return_value = 'application/json'
                client.get_app.side_effect = NotFoundError(response=response_mock)
                with self.assertRaises(NotFoundError):
                    list(request_parser.split())

    @with_json_fixture('requests/get-v2apps-all-apps.json')
    def test_a_request_with_n_apps_returns_n_marathonapps(self, fixture):
        with application.test_request_context('/v2/apps/', method='GET') as ctx:
            request_parser = RequestParser(ctx.request)
            with RequestsMock() as rsps:
                rsps.add(method='GET',
                         url=conf.MARATHON_ENDPOINT + '/v2/apps',
                         body=json.dumps(fixture),
                         status=200)
                apps = list(request_parser.split())

                request_apps = [request_app for request_app, _ in apps]
                self.assertEqual(request_apps, [MarathonApp()] * 4)

                self.assertEqual([app.id for _, app in apps],
                                 [app['id'] for app in fixture['apps']])

    @with_json_fixture('single_full_app.json')
    def test_a_request_for_a_new_app_will_return_a_tuple_with_an_empty_marathonapp(self, fixture):
        with application.test_request_context('/v2/apps//foo',
                                              method='PUT',
                                              data=json.dumps(fixture)) as ctx:
            request_parser = RequestParser(ctx.request)
            with patch.object(request_parser, 'marathon_client') as client:
                response_mock = Mock()
                response_mock.headers.get.return_value = 'application/json'
                client.get_app.side_effect = NotFoundError(response=response_mock)
                apps = list(request_parser.split())

            self.assertEqual(
                apps,
                [
                    (MarathonApp.from_json(fixture), MarathonApp())
                ]
            )

    @with_json_fixture('single_full_app.json')
    def test_a_request_for_write_operation_with_appid_in_url_path_returns_a_tuple_of_marathonapp(self, fixture):
        scale_up = {'instances': 10}
        with application.test_request_context('/v2/apps/foo',
                                              method='PUT',
                                              data=json.dumps(scale_up)) as ctx:
            request_parser = RequestParser(ctx.request)
            with RequestsMock() as rsps:
                rsps.add(method='GET',
                         url=conf.MARATHON_ENDPOINT + '/v2/apps//foo',
                         body=json.dumps({'app': fixture}),
                         status=200)
                apps = list(request_parser.split())
                expected_app = (MarathonApp(**scale_up), MarathonApp.from_json(fixture))
                self.assertEqual(apps, [expected_app])

    @with_json_fixture('single_full_app.json')
    def test_a_request_for_restart_operation_with_appid_in_url_path_returns_a_tuple_of_marathonapp(self, fixture):
        with application.test_request_context('/v2/apps/xablau/restart',
                                              method='PUT',
                                              data=b'{"force": true}') as ctx:
            request_parser = RequestParser(ctx.request)
            with RequestsMock() as rsps:
                rsps.add(method='GET',
                         url=conf.MARATHON_ENDPOINT + '/v2/apps//xablau',
                         body=json.dumps({'app': fixture}),
                         status=200)
                apps = list(request_parser.split())

                expected_app = (MarathonApp(), MarathonApp.from_json(fixture))
                self.assertEqual(apps, [expected_app])

    @with_json_fixture('single_full_app.json')
    def test_split_does_not_break_when_removing_force_parameter_if_request_is_a_list(self, fixture):
        request_data = {"id": "/foo", "instances": 2}
        with application.test_request_context('/v2/apps/',
                                              method='PUT',
                                              data=json.dumps(request_data)) as ctx:
            request_parser = RequestParser(ctx.request)
            with RequestsMock() as rsps:
                rsps.add(method='GET',
                         url=conf.MARATHON_ENDPOINT + '/v2/apps//foo',
                         body=json.dumps({'app': fixture}),
                         status=200)
                apps = list(request_parser.split())

                expected_app = (MarathonApp.from_json(request_data), MarathonApp.from_json(fixture))
                self.assertEqual(apps, [expected_app])

    def test_it_raises_an_error_if_group_request(self):
        with application.test_request_context('/v2/groups/',
                                              method='PUT', data=b'') as ctx:
            request_parser = RequestParser(ctx.request)
            with self.assertRaises(NotImplementedError):
                list(request_parser.split())


class JoinTests(TestCase):
    @with_json_fixture('single_full_app.json')
    def test_it_recreates_a_get_request_for_a_single_app(self, fixture):
        with application.test_request_context('/v2/apps//foo',
                                              method='GET', data=b'') as ctx:
            request_parser = RequestParser(ctx.request)
            with patch.object(request_parser, 'marathon_client') as client:
                client.get_app.return_value = MarathonApp.from_json(fixture)
                apps = list(request_parser.split())

                request = request_parser.join(apps)
                self.assertIsInstance(request, HollowmanRequest)
                self.assertEqual(request, ctx.request)
                self.assertEqual(request.data, b'')

    @with_json_fixture('single_full_app.json')
    def test_it_recreates_a_put_request_for_a_single_app(self, fixture):
        with application.test_request_context('/v2/apps//foo',
                                              method='PUT',
                                              data=json.dumps(fixture)) as ctx:
            request_parser = RequestParser(ctx.request)
            with patch.object(request_parser, 'marathon_client') as client:
                client.get_app.return_value = MarathonApp.from_json(fixture)
                apps = list(request_parser.split())

                request = request_parser.join(apps)
                self.assertIsInstance(request, HollowmanRequest)
                self.assertEqual(request.get_json()['id'], '/foo')

    @with_json_fixture('single_full_app.json')
    def test_it_recreates_a_post_request_for_a_single_app(self, fixture):
        with application.test_request_context('/v2/apps//foo',
                                              method='POST',
                                              data=json.dumps(fixture)) as ctx:
            request_parser = RequestParser(ctx.request)
            with patch.object(request_parser, 'marathon_client') as client:
                client.get_app.return_value = MarathonApp.from_json(fixture)
                apps = list(request_parser.split())

                request = request_parser.join(apps)
                self.assertIsInstance(request, HollowmanRequest)
                self.assertEqual(request.get_json()['id'], '/foo')

    @with_json_fixture('requests/put-multi-app.json')
    def test_it_recreates_a_put_request_for_multiple_apps(self, fixture):
        with application.test_request_context('/v2/apps/',
                                              method='PUT',
                                              data=json.dumps(fixture)) as ctx:
            request_parser = RequestParser(ctx.request)
            mock_app = get_fixture('single_full_app.json')
            mock_apps = [(MarathonApp.from_json(mock_app), Mock()) for _ in range(2)]

            request = request_parser.join(mock_apps)
            self.assertIsInstance(request, HollowmanRequest)
            self.assertCountEqual(
                [app['id'] for app in json.loads(request.data)],
                [app.id for app, _ in mock_apps]
            )

    def test_it_raises_an_error_if_group_request(self):
        with application.test_request_context('/v2/groups/',
                                              method='PUT', data=b'') as ctx:
            request_parser = RequestParser(ctx.request)
            with self.assertRaises(NotImplementedError):
                request_parser.join([])
