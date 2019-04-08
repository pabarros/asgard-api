import json

import jwt

from asgard.http.auth.jwt import jwt_encode
from asgard.models.account import Account
from asgard.models.user import User
from hollowman.app import application
from hollowman.conf import SECRET_KEY
from itests.util import (
    BaseTestCase,
    USER_WITH_MULTIPLE_ACCOUNTS_DICT,
    USER_WITH_ONE_ACCOUNT_DICT,
    ACCOUNT_DEV_DICT,
    ACCOUNT_INFRA_DICT,
)


class AccountEndpointsTest(BaseTestCase):
    async def setUp(self):
        await super(AccountEndpointsTest, self).setUp()

        self.account_dev = Account(**ACCOUNT_DEV_DICT)
        self.account_infra = Account(**ACCOUNT_INFRA_DICT)

        self.user = User(**USER_WITH_MULTIPLE_ACCOUNTS_DICT)

        self.user_with_one_account = User(**USER_WITH_ONE_ACCOUNT_DICT)

    async def tearDown(self):
        await super(AccountEndpointsTest, self).tearDown()

    def generate_jwt_token_for_user(self, user, account):
        return jwt_encode(user, account)

    def test_get_current_user_info_valid_auth(self):
        with application.app_context(), application.test_client() as client:
            jwt_token = self.generate_jwt_token_for_user(
                self.user, self.account_dev
            )
            response = client.get(
                "/hollow/account/me",
                headers={
                    "Authorization": "JWT {}".format(jwt_token.decode("utf8"))
                },
            )
            self.assertEqual(200, response.status_code)
            response_data = json.loads(response.data)

            self.assertEqual(self.user.email, response_data["user"]["email"])
            self.assertEqual(self.user.name, response_data["user"]["name"])
            self.assertEqual(
                self.account_dev.id, response_data["current_account"]["id"]
            )
            self.assertEqual(
                self.account_dev.name, response_data["current_account"]["name"]
            )

    def test_get_current_user_info_auth_invalid(self):
        with application.app_context(), application.test_client() as client:
            response = client.get("/hollow/account/me")
            self.assertEqual(401, response.status_code)

    def test_change_to_next_account_one_account_left(self):
        """
        User tem duas accounts, está usando a primeira e pede pra trocar para a proxima.
        Retornamos a segunda
        """
        with application.app_context(), application.test_client() as client:
            jwt_token = self.generate_jwt_token_for_user(
                self.user, self.account_dev
            )
            response = client.post(
                "/hollow/account/next",
                headers={
                    "Authorization": "JWT {}".format(jwt_token.decode("utf8"))
                },
            )
            self.assertEqual(200, response.status_code)
            response_data = json.loads(response.data)

            self.assertEqual(self.user.email, response_data["user"]["email"])
            self.assertEqual(self.user.name, response_data["user"]["name"])
            self.assertEqual(
                self.account_infra.id, response_data["current_account"]["id"]
            )
            self.assertEqual(
                self.account_infra.name,
                response_data["current_account"]["name"],
            )

            jwt_response_header = response_data["jwt_token"]
            self.assertTrue(jwt_response_header)
            returned_token = jwt.decode(jwt_response_header, key=SECRET_KEY)
            self.assertEqual(self.user.email, returned_token["user"]["email"])
            self.assertEqual(self.user.name, returned_token["user"]["name"])
            self.assertEqual(
                self.account_infra.id, returned_token["current_account"]["id"]
            )
            self.assertEqual(
                self.account_infra.name,
                returned_token["current_account"]["name"],
            )

    def test_test_change_to_next_account_no_account_left(self):
        """
        User tem duas accounts e já está usando a segunda, quando pedir a próxima
        retornamos a primeira account
        """
        with application.app_context(), application.test_client() as client:
            jwt_token = self.generate_jwt_token_for_user(
                self.user, self.account_infra
            )
            response = client.post(
                "/hollow/account/next",
                headers={
                    "Authorization": "JWT {}".format(jwt_token.decode("utf8"))
                },
            )
            self.assertEqual(200, response.status_code)
            response_data = json.loads(response.data)

            self.assertEqual(self.user.email, response_data["user"]["email"])
            self.assertEqual(self.user.name, response_data["user"]["name"])
            self.assertEqual(
                self.account_dev.id, response_data["current_account"]["id"]
            )
            self.assertEqual(
                self.account_dev.name, response_data["current_account"]["name"]
            )

            jwt_response_header = response_data["jwt_token"]
            self.assertTrue(jwt_response_header)
            returned_token = jwt.decode(jwt_response_header, key=SECRET_KEY)
            self.assertEqual(self.user.email, returned_token["user"]["email"])
            self.assertEqual(self.user.name, returned_token["user"]["name"])
            self.assertEqual(
                self.account_dev.id, returned_token["current_account"]["id"]
            )
            self.assertEqual(
                self.account_dev.name, returned_token["current_account"]["name"]
            )
