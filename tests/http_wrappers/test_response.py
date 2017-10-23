import json
import unittest
from copy import deepcopy
from http import HTTPStatus
from unittest import TestCase
from unittest.mock import patch, Mock, call

from marathon import NotFoundError, MarathonApp
from flask import Response as FlaskResponse
from responses import RequestsMock

from hollowman import conf
from hollowman.app import application
from hollowman.http_wrappers import Response
from hollowman.marathonapp import SieveMarathonApp
from tests.utils import with_json_fixture, get_fixture


class SplitTests(unittest.TestCase):
    def setUp(self):
        self.empty_ok_response = FlaskResponse(
            response=b'{}',
            status=HTTPStatus.OK,
            headers={}
        )

    @with_json_fixture('single_full_app.json')
    def test_a_single_app_response_returns_a_single_marathonapp(self, fixture):
        with application.test_request_context('/v2/apps//foo',
                                              method='GET', data=b'') as ctx:
            flask_response = FlaskResponse(
                response=json.dumps({"app": fixture}),
                status=HTTPStatus.OK,
                headers={})
            response = Response(ctx.request, flask_response)

            with patch.object(response, 'marathon_client') as client:
                client.get_app.return_value = SieveMarathonApp.from_json(fixture)
                apps = list(response.split())
                self.assertEqual([call("/foo")], client.get_app.call_args_list)

            self.assertEqual(
                apps,
                [
                    (SieveMarathonApp.from_json(fixture), client.get_app.return_value)
                ])

    @with_json_fixture('single_full_app.json')
    def test_multiapp_response_returns_multiple_marathonapp_instances(self, fixture):
        modified_app = fixture.copy()
        modified_app['id'] = '/xablau'

        apps = [fixture, modified_app]
        with application.test_request_context('/v2/apps/',
                                              method='GET', data=b'') as ctx:
            response = FlaskResponse(response=json.dumps({"apps": apps}),
                                     status=HTTPStatus.OK,
                                     headers={})
            response = Response(ctx.request, response)

        with patch.object(response, 'marathon_client') as client:
            original_apps = [MarathonApp.from_json(app) for app in apps]
            client.get_app.side_effect = original_apps
            apps = list(response.split())
            self.assertEqual([call("/foo"), call("/xablau")], client.get_app.call_args_list)

        self.assertEqual(
            apps,
            [
                (SieveMarathonApp.from_json(fixture), original_apps[0]),
                (SieveMarathonApp.from_json(modified_app), original_apps[1])
            ]
        )

    @with_json_fixture('single_full_app.json')
    def test_a_response_for_restart_operation_with_appid_in_url_path_returns_a_tuple_of_marathonapp(self, fixture):
        with application.test_request_context('/v2/apps/xablau/restart',
                                              method='PUT',
                                              data=b'{"force": true}') as ctx:
            response = FlaskResponse(
                response=b"{}",
                status=HTTPStatus.OK,
                headers={}
            )
            response = Response(ctx.request, response)
            with RequestsMock() as rsps:
                rsps.add(method='GET',
                         url=conf.MARATHON_ENDPOINT + '/v2/apps//xablau',
                         body=json.dumps({'app': fixture}),
                         status=200)
                apps = list(response.split())

                self.assertEqual(apps, [
                    (SieveMarathonApp(), SieveMarathonApp.from_json(fixture))
                ])

    @with_json_fixture('single_full_app.json')
    def test_a_response_for_write_operation_with_appid_in_url_path_returns_a_tuple_of_marathonapp(self, fixture):
        scale_up = {'instances': 10}
        with application.test_request_context('/v2/apps//foo',
                                              method='PUT',
                                              data=json.dumps(scale_up)) as ctx:
            response = FlaskResponse(
                response=b'{}',
                status=HTTPStatus.OK,
                headers={}
            )
            response = Response(ctx.request, response)
            with RequestsMock() as rsps:
                rsps.add(method='GET',
                         url=conf.MARATHON_ENDPOINT + '/v2/apps//foo',
                         body=json.dumps({'app': fixture}),
                         status=200)
                apps = list(response.split())

                self.assertEqual(apps, [
                    (SieveMarathonApp(), SieveMarathonApp.from_json(fixture))
                ])

    @unittest.skip("Pode ser que esse teste nao faça sentido, já que PUT em /v2/apps/ retorna um Deployment")
    @with_json_fixture('single_full_app.json')
    def test_a_response_for_write_operation_on_multiple_apps_on_root_path_returns_tuples_of_marathonapp(self, fixture):
        request_data = [
            {
                "id": "/foo",
                "cmd": "sleep 60",
                "cpus": 0.3,
                "instances": 2,
                "mem": 9,
                "dependencies": [
                    "/test/sleep120",
                    "/other/namespace/or/app"
                ]
            },
            {
                "id": "/xablau",
                "cmd": "sleep 120",
                "cpus": 0.3,
                "instances": 2,
                "mem": 9
            }
        ]
        with application.test_request_context('/v2/apps/',
                                              method='PUT',
                                              data=json.dumps(request_data)) as ctx:
            response = FlaskResponse(
                response=b'{}',
                status=HTTPStatus.OK,
                headers={}
            )
            response = Response(ctx.request, response)
            with RequestsMock() as rsps:
                rsps.add(method='GET',
                         url=conf.MARATHON_ENDPOINT + '/v2/apps//foo',
                         body=json.dumps({'app': deepcopy(fixture)}),
                         status=200)
                xablau_app = deepcopy(fixture)
                xablau_app['id'] = '/xablau'
                rsps.add(method='GET',
                         url=conf.MARATHON_ENDPOINT + '/v2/apps//xablau',
                         body=json.dumps({'app': xablau_app}),
                         status=200)
                apps = list(response.split())

            self.assertEqual(apps, [
                (SieveMarathonApp(), SieveMarathonApp.from_json(fixture)),
                (SieveMarathonApp(), SieveMarathonApp.from_json(xablau_app))
            ])

class JoinTests(unittest.TestCase):
    @with_json_fixture('single_full_app.json')
    def test_it_recreates_a_get_response_for_a_single_app(self, fixture):
        with application.test_request_context('/v2/apps//foo',
                                              method='GET', data=b'') as ctx:
            response = FlaskResponse(response=json.dumps({"app": fixture}),
                                     status=HTTPStatus.OK,
                                     headers={})
            response = Response(ctx.request, response)

        with patch.object(response, 'marathon_client') as client:
            client.get_app.return_value = SieveMarathonApp.from_json(deepcopy(fixture))
            apps = list(response.split())

            joined_response = response.join(apps)

            self.assertIsInstance(joined_response, FlaskResponse)
            self.assertDictEqual(json.loads(joined_response.data), {'app': fixture})

    @with_json_fixture('single_full_app.json')
    def test_it_recreates_a_get_response_for_multiple_apps(self, fixture):
        modified_app = deepcopy(fixture)
        modified_app['id'] = '/xablau'

        fixtures = [fixture, modified_app]
        expected_response = deepcopy(fixtures)
        with application.test_request_context('/v2/apps/',
                                              method='GET', data=b'') as ctx:
            response = FlaskResponse(response=json.dumps({"apps": fixtures}),
                                     status=HTTPStatus.OK,
                                     headers={})
            response = Response(ctx.request, response)

        with patch.object(response, 'marathon_client') as client:
            original_apps = [SieveMarathonApp.from_json(app) for app in fixtures]
            client.get_app.side_effect = original_apps
            apps = list(response.split())

            joined_response = response.join(apps)

            self.assertIsInstance(joined_response, FlaskResponse)
            self.assertDictEqual(json.loads(joined_response.data),
                                 {'apps': expected_response})

    @with_json_fixture("single_full_app.json")
    def test_should_join_an_empty_list_into_an_empty_response_single_app(self, single_full_app_fixture):
        with application.test_request_context('/v2/apps//foo',
                                              method='GET', data=b'') as ctx:
            response = FlaskResponse(response=json.dumps({"app": single_full_app_fixture}),
                                     status=HTTPStatus.OK,
                                     headers={})
            response = Response(ctx.request, response)

            joined_response = response.join([])

            self.assertIsInstance(joined_response, FlaskResponse)
            self.assertDictEqual(json.loads(joined_response.data), {'app': {}})

    @with_json_fixture("single_full_app.json")
    def test_should_join_an_empty_list_into_an_empty_response_multi_app(self, single_full_app_fixture):
        modified_app = deepcopy(single_full_app_fixture)
        modified_app['id'] = '/other-app'

        fixtures = [single_full_app_fixture, modified_app]
        expected_response = deepcopy(fixtures)
        with application.test_request_context('/v2/apps/',
                                              method='GET', data=b'') as ctx:
            response = FlaskResponse(response=json.dumps({"apps": fixtures}),
                                     status=HTTPStatus.OK,
                                     headers={})
            response = Response(ctx.request, response)

            joined_response = response.join([])

            self.assertIsInstance(joined_response, FlaskResponse)
            self.assertDictEqual(json.loads(joined_response.data),
                                 {'apps': []})

