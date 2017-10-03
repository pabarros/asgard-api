
from collections import namedtuple
from mock import patch
from unittest import TestCase, skip
import responses
import json

from hollowman.app import application
from hollowman import conf
from hollowman import decorators
import hollowman.upstream
from hollowman.models import HollowmanSession, User

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
        self.session.add(User(tx_email="user@host.com.br", tx_name="John Doe", tx_authkey="69ed620926be4067a36402c3f7e9ddf0"))
        self.session.commit()
        responses.add(method='GET',
                         url=conf.MARATHON_ENDPOINT + '/v2/apps',
                         body=json.dumps({'apps': [fixture]}),
                         status=200)
        responses.start()

    def tearDown(self):
        self.session.close()
        responses.stop()

    def test_remove_transfer_encoding_header(self):
        mock_response = DummyResponse(headers={"Transfer-Encoding": "chunked"})
        with patch.object(hollowman.upstream, 'replay_request', return_value=mock_response) as replay_mock, \
             application.test_client() as client, \
             patch.multiple(decorators, HOLLOWMAN_ENFORCE_AUTH=False):
                response = client.get("/v2/apps")
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
