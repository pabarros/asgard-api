from unittest import TestCase, skip
from unittest.mock import patch, ANY, MagicMock
import responses
import json

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
            with patch('hollowman.request_handlers.upstream_request'):
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
            with patch('hollowman.request_handlers.upstream_request'):
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
            with patch('hollowman.request_handlers.upstream_request'):
                request_parser = Request(ctx.request)
                request_parser.split = MagicMock(return_value=[self.request_apps[0]])
                request_parser.join = MagicMock()
                response = new(request_parser)
                self.dispatch.assert_called_once_with(operations=ANY,
                                                user=None,
                                                request_app=ANY,
                                                app=ANY)

    @skip("Existe a chance de trocarmos esse teste por um ponta a ponta")
    def test_dispatches_response_pipeline_read_multi_app(self):
        self.fail()

    @skip("Existe a chance de trocarmos esse teste por um ponta a ponta")
    def test_dispatches_response_pipeline_read_single_app(self):
        self.fail()

    @with_json_fixture("single_full_app.json")
    def test_do_not_dispatche_response_pipeline_write_single_app(self, single_full_app_fixture):
        auth_header = {"Authorization": "Token 69ed620926be4067a36402c3f7e9ddf0"}
        with application.test_client() as client:
            with patch('hollowman.request_handlers.dispatch_response_pipeline') as resp_pipeline_mock:
                responses.add(method='GET',
                         url=conf.MARATHON_ENDPOINT + '/v2/apps//foo',
                         body=json.dumps({'app': single_full_app_fixture}),
                         status=200)
                responses.add(method='POST',
                           url=conf.MARATHON_ENDPOINT + '/v2/apps',
                           body=json.dumps({'apps': [single_full_app_fixture]}),
                           status=200)
                response = client.post("/v2/apps/foo", data=json.dumps(single_full_app_fixture), headers=auth_header)
                self.assertEqual(200, response.status_code)
                self.assertEqual(0, resp_pipeline_mock.call_count)

    @with_json_fixture("single_full_app.json")
    def test_do_not_dispatche_response_pipeline_write_multi_app(self, single_full_app_fixture):
        auth_header = {"Authorization": "Token 69ed620926be4067a36402c3f7e9ddf0"}
        with application.test_client() as client:
            with patch('hollowman.request_handlers.dispatch_response_pipeline') as resp_pipeline_mock:
                responses.add(method='GET',
                         url=conf.MARATHON_ENDPOINT + '/v2/apps//foo',
                         body=json.dumps({'app': single_full_app_fixture}),
                         status=200)
                responses.add(method='POST',
                           url=conf.MARATHON_ENDPOINT + '/v2/apps',
                           body=json.dumps({}),
                           status=200)
                response = client.post("/v2/apps/foo", data=json.dumps([single_full_app_fixture]), headers=auth_header)
                self.assertEqual(200, response.status_code)
                self.assertEqual(0, resp_pipeline_mock.call_count)

