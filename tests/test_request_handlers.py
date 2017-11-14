from unittest import TestCase, skip
from unittest.mock import patch, ANY, MagicMock
import responses
from responses import RequestsMock
import json
from copy import deepcopy

from marathon import MarathonApp

from hollowman.app import application
from hollowman.request_handlers import new
from hollowman.models import HollowmanSession, User, Account
from hollowman.http_wrappers.request import Request
from hollowman import conf

from tests import rebuild_schema
from tests.utils import with_json_fixture

class RequestHandlersTests(TestCase):

    @with_json_fixture("single_full_app.json")
    def setUp(self, single_full_app_fixture):
        self.parser = MagicMock()
        self.parser.return_value.is_group_request.return_value = False

        self.request_apps = [
            (MarathonApp(id='/xablau'), MarathonApp(id='/xena')),
            (MarathonApp(id='/foo'), MarathonApp(id='/bar')),
        ]
        self.parser.return_value.split.return_value = self.request_apps

        dispatch_patch = patch('hollowman.request_handlers.dispatch',
                               side_effect=lambda *args, **kwargs: kwargs['request_app'])
        self.dispatch = dispatch_patch.start()

        rebuild_schema()
        self.session = HollowmanSession()
        self.user = User(tx_email="user@host.com.br", tx_name="John Doe", tx_authkey="69ed620926be4067a36402c3f7e9ddf0")
        self.account_dev = Account(id=4, name="Dev Team", namespace="dev", owner="company")
        self.user.accounts = [self.account_dev]
        self.session.add(self.user)
        self.session.add(self.account_dev)
        self.session.commit()
        responses.add(method='POST',
                         url=conf.MARATHON_ENDPOINT + '/v2/apps/foo',
                         body=json.dumps({'apps': [single_full_app_fixture]}),
                         status=200)
        responses.add(method='GET',
                         url=conf.MARATHON_ENDPOINT + '/v2/apps/foo',
                         body=json.dumps(single_full_app_fixture),
                         status=200)
        responses.start()

    def tearDown(self):
        responses.stop()
        patch.stopall()

    def test_it_dispatches_apps_from_request(self):
        with application.test_request_context('/v2/apps/foo', method='GET') as ctx:
            with patch('hollowman.request_handlers.upstream_request'), \
                 patch('hollowman.request_handlers.dispatch_response_pipeline'):
                request_parser = Request(ctx.request)
                request_parser.split = MagicMock(return_value=self.request_apps)
                request_parser.join = MagicMock()
                response = new(request_parser)

                request_parser.split.assert_called_once()
                request_parser.join.assert_called_once_with(self.request_apps)

    def test_it_call_dispatch_using_user_from_request(self):
        """
        Certificamos que o user preenchido no request é repassado para o dispatch
        """
        with application.test_request_context('/v2/apps/foo', method='GET') as ctx:
            with patch('hollowman.request_handlers.upstream_request'), \
                 patch('hollowman.request_handlers.dispatch_response_pipeline'):
                user = MagicMock()
                ctx.request.user = user
                request_parser = Request(ctx.request)
                request_parser.split = MagicMock(return_value=[self.request_apps[0]])
                request_parser.join = MagicMock()
                response = new(request_parser)
                self.dispatch.assert_called_once_with(operations=ANY,
                                                user=user,
                                                request_app=ANY,
                                                app=ANY)

    def test_it_calls_dispatch_with_user_none_if_not_authenticated(self):
        with application.test_request_context('/v2/apps/foo', method='GET') as ctx:
            with patch('hollowman.request_handlers.upstream_request'), \
                 patch('hollowman.request_handlers.dispatch_response_pipeline'):
                request_parser = Request(ctx.request)
                request_parser.split = MagicMock(return_value=[self.request_apps[0]])
                request_parser.join = MagicMock()
                response = new(request_parser)
                self.dispatch.assert_called_once_with(operations=ANY,
                                                user=None,
                                                request_app=ANY,
                                                app=ANY)

    @with_json_fixture("single_full_app.json")
    def test_do_not_dispatch_response_pipeline_write_single_app(self, single_full_app_fixture):
        auth_header = {"Authorization": "Token 69ed620926be4067a36402c3f7e9ddf0"}
        with application.test_client() as client:
            with patch('hollowman.request_handlers.dispatch_response_pipeline') as resp_pipeline_mock:
                with RequestsMock() as rsps:
                    rsps.add(method='GET', url=conf.MARATHON_ENDPOINT + '/v2/apps//dev/foo',
                             body=json.dumps({'app': single_full_app_fixture}), status=200)
                    rsps.add(method='POST', url=conf.MARATHON_ENDPOINT + '/v2/apps/foo',
                               body=json.dumps({'apps': [single_full_app_fixture]}), status=200)
                    response = client.post("/v2/apps/foo", data=json.dumps(single_full_app_fixture), headers=auth_header)
                    self.assertEqual(200, response.status_code)
                    self.assertEqual(0, resp_pipeline_mock.call_count)

    @with_json_fixture("single_full_app.json")
    def test_do_not_dispatch_response_pipeline_write_multi_app(self, single_full_app_fixture):
        auth_header = {"Authorization": "Token 69ed620926be4067a36402c3f7e9ddf0"}
        with application.test_client() as client:
            with patch('hollowman.request_handlers.dispatch_response_pipeline') as resp_pipeline_mock:
                responses.add(method='GET', url=conf.MARATHON_ENDPOINT + '/v2/apps//dev/foo',
                         body=json.dumps({'app': single_full_app_fixture}), status=200)
                responses.add(method='POST', url=conf.MARATHON_ENDPOINT + '/v2/apps/',
                           body=json.dumps({}), status=200)
                response = client.post("/v2/apps/", data=json.dumps([single_full_app_fixture]), headers=auth_header)
                self.assertEqual(200, response.status_code)
                self.assertEqual(0, resp_pipeline_mock.call_count)

    @with_json_fixture("../fixtures/single_full_app.json")
    def test_versions_endpoint_returns_app_on_root_json(self, single_full_app_fixture):
        """
        Apesar de um GET /v2/apps/<app-id> retornat a app em:
            {"app": <app-definition}
        um GET /v2/apps/<app-id>/versions/<version-id> retorna em:
            {<app-definition>}

        Aqui conferimos que nosso pipeline retorna um response consistente com
        essa regra
        """
        auth_header = {"Authorization": "Token 69ed620926be4067a36402c3f7e9ddf0"}
        single_full_app_fixture['id'] = "/dev/foo"
        with application.test_client() as client:
            with RequestsMock() as rsps:
                rsps.add(method='GET', url=conf.MARATHON_ENDPOINT + '/v2/apps/dev/foo/versions/2017-10-31T13:01:07.768Z',
                         body=json.dumps(single_full_app_fixture), status=200)
                rsps.add(method='GET', url=conf.MARATHON_ENDPOINT + '/v2/apps//dev/foo',
                         body=json.dumps({"app": single_full_app_fixture}), status=200)
                response = client.get("/v2/apps/foo/versions/2017-10-31T13:01:07.768Z", headers=auth_header)
                self.assertEqual(200, response.status_code)
                self.assertEqual("/foo", json.loads(response.data)['id'])

    @with_json_fixture("../fixtures/group_dev_namespace_with_apps.json")
    def test_groups_endpoint_returns_group_on_root_json(self, group_dev_namespace_fixture):
        auth_header = {"Authorization": "Token 69ed620926be4067a36402c3f7e9ddf0"}
        with application.test_client() as client:
            with RequestsMock() as rsps:
                rsps.add(method='GET', url=conf.MARATHON_ENDPOINT + '/v2/groups//dev/group-b',
                         body=json.dumps(deepcopy(group_dev_namespace_fixture['groups'][1])), status=200)
                rsps.add(method='GET', url=conf.MARATHON_ENDPOINT + '/v2/groups/dev/group-b',
                         body=json.dumps(deepcopy(group_dev_namespace_fixture['groups'][1])), status=200)
                rsps.add(method='GET', url=conf.MARATHON_ENDPOINT + '/v2/groups//dev/group-b/group-b0',
                         body=json.dumps(deepcopy(group_dev_namespace_fixture['groups'][1]['groups'][0])), status=200)
                response = client.get("/v2/groups/group-b", headers=auth_header)
                self.assertEqual(200, response.status_code)
                self.assertEqual("/group-b", json.loads(response.data)['id'])

    @with_json_fixture("../fixtures/queue/get.json")
    def test_queue_removes_queued_appps_from_other_namespaces(self, queue_get_fixture):
        """
        Removemos todas as apps que não sejam do namespace atual.
        Esse teste tambéem confirma que o namespace é removido dos elementos
        que voltam no response.
        """
        auth_header = {"Authorization": "Token 69ed620926be4067a36402c3f7e9ddf0"}
        with application.test_client() as client:
            with RequestsMock() as rsps:
                rsps.add(method='GET',
                         url=conf.MARATHON_ENDPOINT + '/v2/queue',
                         status=200,
                         body=json.dumps(queue_get_fixture))

                response = client.get("/v2/queue", headers=auth_header)
                self.assertEqual(200, response.status_code)
                response_data = json.loads(response.data)
                self.assertEqual(1, len(response_data['queue']))
                self.assertEqual("/waiting", response_data['queue'][0]['app']['id'])

class DispatchResponse404Test(TestCase):

    @with_json_fixture("single_full_app.json")
    def setUp(self, single_full_app_fixture):
        self.parser = MagicMock()
        self.parser.return_value.is_group_request.return_value = False

        self.request_apps = [
            (MarathonApp(id='/xablau'), MarathonApp(id='/xena')),
            (MarathonApp(id='/foo'), MarathonApp(id='/bar')),
        ]
        self.parser.return_value.split.return_value = self.request_apps

        dispatch_patch = patch('hollowman.request_handlers.dispatch',
                               side_effect=lambda *args, **kwargs: kwargs['request_app'])
        self.dispatch = dispatch_patch.start()

        rebuild_schema()
        self.session = HollowmanSession()
        self.user = User(tx_email="user@host.com.br", tx_name="John Doe", tx_authkey="69ed620926be4067a36402c3f7e9ddf0")
        self.account_dev = Account(id=4, name="Dev Team", namespace="dev", owner="company")
        self.user.accounts = [self.account_dev]
        self.session.add(self.user)
        self.session.add(self.account_dev)
        self.session.commit()

    def test_do_not_dispatch_response_pipeline_if_upstream_returns_404(self):
        auth_header = {"Authorization": "Token 69ed620926be4067a36402c3f7e9ddf0"}
        with application.test_client() as client:
            with patch('hollowman.request_handlers.dispatch_response_pipeline') as resp_pipeline_mock:
                with RequestsMock() as rsps:
                    rsps.add(method='GET', url=conf.MARATHON_ENDPOINT + '/v2/apps//dev/foo',
                             body=json.dumps({'message': "App /foo not found"}), status=404)
                    rsps.add(method='GET', url=conf.MARATHON_ENDPOINT + '/v2/apps/dev/foo',
                             body=json.dumps({'message': "App /foo not found"}), status=404)
                    response = client.get("/v2/apps/foo", headers=auth_header)
                    self.assertEqual(404, response.status_code)
                    self.assertEqual(0, resp_pipeline_mock.call_count)

