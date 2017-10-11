from unittest import TestCase
from unittest.mock import patch, ANY, MagicMock
import responses
import json

from marathon import MarathonApp

from hollowman.app import application
from hollowman.request_handlers import new
from hollowman.models import HollowmanSession, User, Account
from hollowman.parsers import RequestParser
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
                request_parser = RequestParser(ctx.request)
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
                request_parser = RequestParser(ctx.request)
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
                request_parser = RequestParser(ctx.request)
                request_parser.split = MagicMock(return_value=[self.request_apps[0]])
                request_parser.join = MagicMock()
                response = new(request_parser)
                self.dispatch.assert_called_once_with(operations=ANY,
                                                user=None,
                                                request_app=ANY,
                                                app=ANY)
