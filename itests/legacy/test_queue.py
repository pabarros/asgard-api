import json
from typing import Dict

from responses import RequestsMock

from hollowman import conf
from hollowman.app import application
from hollowman.auth.jwt import jwt_auth, jwt_generate_user_info
from itests.util import BaseTestCase, USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY
from tests.utils import with_json_fixture


class DeploymentsTests(BaseTestCase):
    async def setUp(self):
        await super(DeploymentsTests, self).setUp()
        self.auth_header = {
            "Authorization": f"Token {USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY}"
        }

    def make_auth_header(self, user, account) -> Dict[str, str]:
        jwt_token = jwt_auth.jwt_encode_callback(
            jwt_generate_user_info(user, account)
        )
        return {"Authorization": "JWT {}".format(jwt_token.decode("utf-8"))}

    @with_json_fixture("../fixtures/queue/get.json")
    def test_v2_queue_get(self, fixture):
        with application.test_client() as client, RequestsMock() as rsps:
            rsps.add(
                url=f"{conf.MARATHON_ADDRESSES[0]}/v2/queue",
                body=json.dumps(fixture),
                method="GET",
                status=200,
            )
            response = client.get("/v2/queue", headers=self.auth_header)
            response_data = json.loads(response.data)
            self.assertEqual(1, len(response_data["queue"]))
            self.assertEqual("/waiting", response_data["queue"][0]["app"]["id"])
