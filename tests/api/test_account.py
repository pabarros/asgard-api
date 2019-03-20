import json
import unittest

import jwt

from asgard.models.account import AccountDB as Account
from hollowman.app import application
from hollowman.auth.jwt import jwt_auth, jwt_generate_user_info
from hollowman.conf import SECRET_KEY
from hollowman.models import HollowmanSession, User
from tests import rebuild_schema
from tests.utils import with_json_fixture


class TestAccountEndpoints(unittest.TestCase):
    def setUp(self):
        rebuild_schema()
        self.session = HollowmanSession()

        self.account_dev = Account(
            id=4, name="Dev Team", namespace="dev", owner="company"
        )
        self.account_infra = Account(
            name="Infra Team", namespace="infra", owner="company"
        )

        self.user = User(tx_email="user@host.com.br", tx_name="John Doe")
        self.user.accounts = [self.account_dev, self.account_infra]

        self.user_with_one_account = User(
            tx_email="user-one-account@host.com.br", tx_name="User One Account"
        )
        self.user_with_one_account.accounts = [self.account_dev]

        self.session.add(self.account_dev)
        self.session.add(self.account_infra)

        self.session.add(self.user)
        self.session.add(self.user_with_one_account)
        self.session.commit()

    def tearDown(self):
        self.session.close()

    def generate_jwt_token_for_user(self, user, account):
        return jwt_auth.jwt_encode_callback(
            jwt_generate_user_info(user, account)
        )

    def test_get_current_user_info_valid_auth(self):
        with application.app_context(), application.test_client() as client:
            jwt_token = self.generate_jwt_token_for_user(
                self.user, self.user.accounts[0]
            )
            response = client.get(
                "/hollow/account/me",
                headers={
                    "Authorization": "JWT {}".format(jwt_token.decode("utf8"))
                },
            )
            self.assertEqual(200, response.status_code)
            response_data = json.loads(response.data)

            self.assertEqual(self.user.tx_email, response_data["user"]["email"])
            self.assertEqual(self.user.tx_name, response_data["user"]["name"])
            self.assertEqual(
                self.user.accounts[0].id, response_data["current_account"]["id"]
            )
            self.assertEqual(
                self.user.accounts[0].name,
                response_data["current_account"]["name"],
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
                self.user, self.user.accounts[0]
            )
            response = client.post(
                "/hollow/account/next",
                headers={
                    "Authorization": "JWT {}".format(jwt_token.decode("utf8"))
                },
            )
            self.assertEqual(200, response.status_code)
            response_data = json.loads(response.data)

            self.assertEqual(self.user.tx_email, response_data["user"]["email"])
            self.assertEqual(self.user.tx_name, response_data["user"]["name"])
            self.assertEqual(
                self.user.accounts[1].id, response_data["current_account"]["id"]
            )
            self.assertEqual(
                self.user.accounts[1].name,
                response_data["current_account"]["name"],
            )

            jwt_response_header = response_data["jwt_token"]
            self.assertTrue(jwt_response_header)
            returned_token = jwt.decode(jwt_response_header, key=SECRET_KEY)
            self.assertEqual(
                self.user.tx_email, returned_token["user"]["email"]
            )
            self.assertEqual(self.user.tx_name, returned_token["user"]["name"])
            self.assertEqual(
                self.user.accounts[1].id,
                returned_token["current_account"]["id"],
            )
            self.assertEqual(
                self.user.accounts[1].name,
                returned_token["current_account"]["name"],
            )

    def test_test_change_to_next_account_no_account_left(self):
        """
        User tem duas accounts e já está usando a segunda, quando pedir a próxima
        retornamos a primeira account
        """
        with application.app_context(), application.test_client() as client:
            jwt_token = self.generate_jwt_token_for_user(
                self.user, self.user.accounts[1]
            )
            response = client.post(
                "/hollow/account/next",
                headers={
                    "Authorization": "JWT {}".format(jwt_token.decode("utf8"))
                },
            )
            self.assertEqual(200, response.status_code)
            response_data = json.loads(response.data)

            self.assertEqual(self.user.tx_email, response_data["user"]["email"])
            self.assertEqual(self.user.tx_name, response_data["user"]["name"])
            self.assertEqual(
                self.user.accounts[0].id, response_data["current_account"]["id"]
            )
            self.assertEqual(
                self.user.accounts[0].name,
                response_data["current_account"]["name"],
            )

            jwt_response_header = response_data["jwt_token"]
            self.assertTrue(jwt_response_header)
            returned_token = jwt.decode(jwt_response_header, key=SECRET_KEY)
            self.assertEqual(
                self.user.tx_email, returned_token["user"]["email"]
            )
            self.assertEqual(self.user.tx_name, returned_token["user"]["name"])
            self.assertEqual(
                self.user.accounts[0].id,
                returned_token["current_account"]["id"],
            )
            self.assertEqual(
                self.user.accounts[0].name,
                returned_token["current_account"]["name"],
            )
