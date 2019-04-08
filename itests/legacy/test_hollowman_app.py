import json

import responses
from mock import patch
from responses import RequestsMock

from asgard.models.account import AccountDB
from asgard.models.user import UserDB
from hollowman import conf
from hollowman.app import application
from hollowman.upstream import replay_request
from itests.util import BaseTestCase
from tests.utils import get_fixture


class DummyResponse(object):
    def __init__(self, headers={}):
        self.headers = headers
        self.content = None
        self.status_code = 200


class HollowmanAppTest(BaseTestCase):
    async def setUp(self):
        await super(HollowmanAppTest, self).setUp()
        fixture = get_fixture("single_full_app.json")
        self.user = UserDB(
            tx_email="user@host.com.br",
            tx_name="John Doe",
            tx_authkey="69ed620926be4067a36402c3f7e9ddf0",
        )
        self.account_dev = AccountDB(
            id=4, name="Dev Team", namespace="dev", owner="company"
        )
        responses.add(
            method="GET",
            url=conf.MARATHON_ADDRESSES[0] + "/v2/apps",
            body=json.dumps({"apps": [fixture]}),
            status=200,
            headers={"Content-Encoding": "chunked"},
        )
        responses.start()

    async def tearDown(self):
        await super(HollowmanAppTest, self).tearDown()
        responses.stop()

    def test_auth_error_returns_HTTP_401(self):
        with application.test_client() as client:
            response = client.get("/v2/apps")
            self.assertEqual(401, response.status_code)

    def test_unexpected_error_returns_HTTP_500(self):
        with application.test_client() as client, RequestsMock():
            response = client.get(
                "/v2/apps",
                headers={
                    "Authorization": "Token 69ed620926be4067a36402c3f7e9ddf0"
                },
            )
            self.assertEqual(500, response.status_code)
            self.assertEqual(
                "No remaining Marathon servers to try",
                json.loads(response.data)["message"],
            )

    def test_remove_transfer_encoding_header(self):
        with application.test_request_context("/v2/apps", method="GET") as ctx:
            response = replay_request(ctx.request)
            self.assertTrue("Content-Encoding" not in response.headers)
            self.assertEqual(200, response.status_code)

    def test_index_path(self):
        response = application.test_client().get("/")

        self.assertEqual(response.status_code, 302)
        self.assertTrue("Location" in response.headers)
        self.assertEqual(
            "http://localhost/v2/apps", response.headers["Location"]
        )

        redirect_value = "https://marathon.sieve.com.br"
        with patch.object(
            conf, "REDIRECT_ROOTPATH_TO", new=redirect_value
        ) as redirect_mock:
            response = application.test_client().open("/")

            self.assertEqual(response.status_code, 302)
            self.assertTrue("Location" in response.headers)
            self.assertEqual(redirect_value, response.headers["Location"])
