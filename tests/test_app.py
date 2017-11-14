
from collections import namedtuple
from mock import patch
from unittest import TestCase, skip
import responses
import json

from hollowman.app import application
from hollowman import conf
from hollowman import decorators
import hollowman.upstream
from hollowman.upstream import replay_request
from hollowman.models import HollowmanSession, User, Account

from tests import rebuild_schema
from tests.utils import with_json_fixture

class DummyResponse(object):

    def __init__(self, headers={}):
        self.headers = headers
        self.content = None
        self.status_code = 200


class TestApp(TestCase):

    @with_json_fixture("single_full_app.json")
    def setUp(self, fixture):
        rebuild_schema()
        self.session = HollowmanSession()
        self.user = User(tx_email="user@host.com.br", tx_name="John Doe", tx_authkey="69ed620926be4067a36402c3f7e9ddf0")
        self.session.add(self.user)
        self.account_dev = Account(id=4, name="Dev Team", namespace="dev", owner="company")
        self.session.add(self.account_dev)
        self.user.accounts = [self.account_dev]
        self.session.commit()
        responses.add(method='GET',
                         url=conf.MARATHON_ENDPOINT + '/v2/apps',
                         body=json.dumps({'apps': [fixture]}),
                         status=200,
                         headers={"Content-Encoding": "chunked"})
        responses.start()

    def tearDown(self):
        self.session.close()
        responses.stop()

    def test_auth_error_returns_HTTP_401(self):
        with application.test_client() as client:
            response = client.get("/v2/apps")
            self.assertEqual(401, response.status_code)

    def test_unexpected_error_returns_HTTP_500(self):
        self.fail()

    def test_remove_transfer_encoding_header(self):
        with application.test_request_context("/v2/apps", method="GET") as ctx:
            response = replay_request(ctx.request, conf.MARATHON_ENDPOINT)
            self.assertTrue("Content-Encoding" not in response.headers)
            self.assertEqual(200, response.status_code)

    def test_index_path(self):
        response = application.test_client().get('/')

        self.assertEqual(response.status_code, 302)
        self.assertTrue('Location' in response.headers)
        self.assertEqual("http://localhost/v2/apps", response.headers['Location'])

        redirect_value = "https://marathon.sieve.com.br"
        with patch.object(conf, "REDIRECT_ROOTPATH_TO", new=redirect_value) as redirect_mock:
            response = application.test_client().open('/')

            self.assertEqual(response.status_code, 302)
            self.assertTrue('Location' in response.headers)
            self.assertEqual(redirect_value, response.headers['Location'])

    @skip('Need to find a way to test this. Any ideas ?')
    def test_apiv2_path(self):
        pass

    def test_fail_healthcheck(self):
        Response = namedtuple('Response', ["status_code"])

        with patch('hollowman.routes.requests.get') as get_mock:
            get_mock.return_value = Response(status_code=404)
            response = application.test_client().open('/healthcheck')
            self.assertEqual(response.status_code, 404)

    def test_200_healthcheck(self):
        Response = namedtuple('Response', ["status_code"])

        with patch('hollowman.routes.requests.get') as get_mock:
            get_mock.return_value = Response(status_code=200)
            response = application.test_client().open('/healthcheck')
            self.assertEqual(response.status_code, 200)
