import json
import unittest

import jwt
import responses
from flask import request
from mock import MagicMock, patch

from asgard.http.auth.jwt import jwt_encode
from asgard.models.account import AccountDB, Account
from asgard.models.user import UserDB, User
from hollowman import conf, decorators, routes
from hollowman.app import application
from hollowman.auth.jwt import jwt_auth, jwt_generate_user_info
from itests.util import (
    BaseTestCase,
    ACCOUNT_DEV_DICT,
    ACCOUNT_INFRA_DICT,
    ACCOUNT_WITH_NO_USERS_DICT,
    USER_WITH_NO_ACCOUNTS_AUTH_KEY,
    USER_WITH_MULTIPLE_ACCOUNTS_DICT,
    USER_WITH_MULTIPLE_ACCOUNTS_NAME,
    USER_WITH_MULTIPLE_ACCOUNTS_EMAIL,
    USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY,
    USER_WITH_NO_ACCOUNTS_DICT,
)
from tests.utils import get_fixture


class AuthenticationTest(BaseTestCase):
    async def setUp(self):
        await super(AuthenticationTest, self).setUp()
        fixture = get_fixture("single_full_app.json")
        self.user = User(**USER_WITH_MULTIPLE_ACCOUNTS_DICT)
        self.account_dev = Account(**ACCOUNT_DEV_DICT)
        self.account_infra = Account(**ACCOUNT_INFRA_DICT)
        self.account_sup = AccountDB(
            name="Support Team", namespace="sup", owner="company"
        )
        # self.user.accounts = [self.account_dev, self.account_infra]
        # self.session.add(self.user)
        # self.session.add(self.account_dev)
        # self.session.add(self.account_infra)
        # self.session.add(self.account_sup)
        self.user_with_no_accounts = User(**USER_WITH_NO_ACCOUNTS_DICT)
        self.account_with_no_user = Account(**ACCOUNT_WITH_NO_USERS_DICT)
        self.response_http_200 = MagicMock(status_code=200)
        responses.add(
            method="GET",
            url=conf.MARATHON_ADDRESSES[0] + "/v2/apps",
            body=json.dumps({"apps": [fixture]}),
            status=200,
        )
        responses.add(
            method="GET",
            url=conf.MARATHON_ADDRESSES[0] + "/v2/groups//dev/",
            body=json.dumps({"apps": [fixture]}),
            status=200,
        )
        responses.add(
            method="GET",
            url=conf.MARATHON_ADDRESSES[0] + "/v2/groups//infra/",
            body=json.dumps({"apps": [fixture]}),
            status=200,
        )
        responses.add(
            method="GET",
            url=conf.MARATHON_ADDRESSES[0] + "/v2/apps//foo",
            body=json.dumps({"app": fixture}),
            status=200,
        )
        responses.start()

    async def tearDown(self):
        await super(AuthenticationTest, self).tearDown()
        responses.stop()

    def auth_header(self, token):
        return {"Authorization": f"Token {token}"}

    def test_populate_request_user_if_key_is_valid(self):
        """
        Populates request.user if authentication is successful
        """
        with application.test_client() as client:
            r = client.get(
                "/v2/apps",
                headers=self.auth_header(USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY),
            )
            self.assertEqual(200, r.status_code)
            self.assertEqual(
                USER_WITH_MULTIPLE_ACCOUNTS_EMAIL, request.user.tx_email
            )

    def test_token_populate_default_account_if_request_account_is_empty(self):
        with application.test_client() as client:
            r = client.get(
                "/v2/apps",
                headers=self.auth_header(USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY),
            )
            self.assertEqual(200, r.status_code)
            self.assertEqual(
                USER_WITH_MULTIPLE_ACCOUNTS_EMAIL, request.user.tx_email
            )
            self.assertEqual(
                self.account_dev.id, request.user.current_account.id
            )
            self.assertEqual(
                self.account_dev.namespace,
                request.user.current_account.namespace,
            )
            self.assertEqual(
                self.account_dev.owner, request.user.current_account.owner
            )

    @unittest.skip("Pode não fazer sentido...")
    def test_jwt_populate_default_account_if_request_account_is_empty(self):
        """
        Como quem gera o token JWT é o server e ele *sempre* coloca account_id (Um user sem nennhuma account associada não se loga), esse request nunca vai acontecer.
        Não acontece pois é impossivel gerar um JWT válido sem ter a SECRET_KEY que só o server tem.
        """
        test_client = application.test_client()
        with application.app_context():
            jwt_token = jwt_auth.jwt_encode_callback(
                {"email": "user@host.com.br"}
            )
            auth_header = {
                "Authorization": "JWT {}".format(jwt_token.decode("utf-8"))
            }
            r = test_client.get("/v2/apps", headers=auth_header)
            self.assertEqual(200, r.status_code)
            self.assertEqual(3, r.user.current_account)

    def test_jwt_return_401_if_user_is_not_linked_to_account(self):
        """
        If user tries to access account without being associated to this account
        """
        test_client = application.test_client()
        with application.app_context():
            jwt_token = jwt_encode(self.user, self.account_with_no_user)
            auth_header = {
                "Authorization": "JWT {}".format(jwt_token.decode("utf-8"))
            }
            r = test_client.get("/v2/apps", headers=auth_header)
            self.assertEqual(401, r.status_code)
            self.assertEqual(
                "Permission Denied to access this account",
                json.loads(r.data)["msg"],
            )

    def test_return_200_if_key_found(self):
        with application.test_client() as client:
            r = client.get(
                "/v2/apps",
                headers=self.auth_header(USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY),
            )
            self.assertEqual(200, r.status_code)

    def test_return_401_if_key_not_found(self):
        with application.test_client() as client:
            r = client.get(
                "/v2/apps", headers={"Authorization": "Token token-not-found"}
            )
            self.assertEqual(401, r.status_code)
            self.assertEqual(
                "Authorization token is invalid", json.loads(r.data)["msg"]
            )

    def test_return_401_if_no_token_present(self):
        with application.test_client() as client:
            r = client.get("/v2/apps")
            self.assertEqual(401, r.status_code)
            self.assertEqual(
                "Authorization token is invalid", json.loads(r.data)["msg"]
            )

    def test_jwt_do_not_trigger_token_auth_if_jwt_token_is_present(self):
        """
        Both auth uses the same header: Authorization. Token Auth should *not* be called if current token is JWT
        """
        with application.test_client() as test_client, application.app_context(), patch.object(
            decorators, "HollowmanSession"
        ) as session_mock:
            test_client.get("/v2/apps", headers={"Authorization": "JWT Token"})
            self.assertEqual(0, session_mock.call_count)

    def test_token_return_401_if_user_is_not_associated_to_desired_account(
        self
    ):
        """
        Qualquer request com `?account_id` que o usuário nao esteja vinculado, retorna 401
        """
        account_id = self.account_with_no_user.id
        with application.test_client() as client:
            r = client.get(
                "/v2/apps?account_id={}".format(account_id),
                headers=self.auth_header(USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY),
            )
            self.assertEqual(401, r.status_code)

    def test_return_200_if_jwt_token_valid(self):
        test_client = application.test_client()
        with application.app_context():
            jwt_token = jwt_encode(self.user, self.account_dev)
            auth_header = {
                "Authorization": "JWT {}".format(jwt_token.decode("utf-8"))
            }
            r = test_client.get("/v2/apps", headers=auth_header)
            self.assertEqual(200, r.status_code)

    def test_jwt_populate_request_user_if_token_is_valid(self):
        with application.app_context(), application.test_client() as test_client:
            jwt_token = jwt_encode(self.user, self.account_infra)
            auth_header = {
                "Authorization": "JWT {}".format(jwt_token.decode("utf-8"))
            }
            r = test_client.get("/v2/apps", headers=auth_header)
            self.assertEqual(200, r.status_code)
            self.assertEqual(
                USER_WITH_MULTIPLE_ACCOUNTS_EMAIL, request.user.tx_email
            )
            self.assertEqual(
                self.account_infra.id, request.user.current_account.id
            )

    def test_jwt_auth_with_token_from_session_if_headers_not_present(self):
        """
        Se não encontrarmos o token JWT no header, olhamos na flask session procurando por ele.
        """
        test_client = application.test_client()

        with application.app_context(), patch.object(
            routes,
            "check_authentication_successful",
            return_value={"email": self.user.email},
        ):
            jwt_token = jwt_encode(self.user, self.account_dev)

            with test_client.session_transaction() as flask_session:
                flask_session["jwt"] = jwt_token

            response = test_client.get("/v2/apps")
            self.assertEqual(200, response.status_code)

    @unittest.skip("Ainda nao temos usuarios validos/ativos/invalidos")
    def test_return_401_if_jwt_token_is_valid_but_user_is_invalid(self):
        """
        User could be inactive or does not exist
        """
        self.fail()

    def test_return_401_if_jwt_token_is_invalid(self):
        with application.app_context(), application.test_client() as test_client:
            jwt_token = jwt.encode(
                {"email": "user@host.com.br"}, key="wrong key"
            )
            auth_header = {
                "Authorization": "JWT {}".format(jwt_token.decode("utf-8"))
            }
            r = test_client.get("/v2/apps", headers=auth_header)
            self.assertEqual(401, r.status_code)
            self.assertEqual(
                "Authorization token is invalid", json.loads(r.data)["msg"]
            )

    def test_return_401_if_jwt_token_not_present(self):
        test_client = application.test_client()
        with application.app_context():
            r = test_client.get("/v2/apps")
            self.assertEqual(401, r.status_code)
            self.assertEqual(
                "Authorization token is invalid", json.loads(r.data)["msg"]
            )

    def test_login_failed_invalid_oauth2(self):
        test_client = application.test_client()

        with application.app_context(), patch.object(
            routes, "check_authentication_successful", return_value={}
        ), patch.object(routes, "render_template") as render_mock:
            test_client.get("/authenticate/google")

            render_mock.assert_called_once_with(
                "login-failed.html", reason="Invalid OAuth2 code"
            )

    def test_login_failed_user_not_found(self):
        test_client = application.test_client()

        with application.app_context(), patch.object(
            routes,
            "check_authentication_successful",
            return_value={"email": "not-found@host.com.br"},
        ), patch.object(routes, "render_template") as render_mock:
            test_client.get("/authenticate/google")

            render_mock.assert_called_once_with(
                "login-failed.html", reason="User not found"
            )

    def test_login_failed_user_does_not_have_any_account(self):
        test_client = application.test_client()

        with application.app_context(), patch.object(
            routes,
            "check_authentication_successful",
            return_value={"email": self.user_with_no_accounts.email},
        ), patch.object(routes, "render_template") as render_mock:
            test_client.get("/authenticate/google")

            render_mock.assert_called_once_with(
                "login-failed.html", reason="No associated accounts"
            )

    def test_return_401_user_has_no_associated_account(self):
        with application.test_client() as client:
            r = client.get(
                "/v2/apps",
                headers=self.auth_header(USER_WITH_NO_ACCOUNTS_AUTH_KEY),
            )
            self.assertEqual(401, r.status_code)
            self.assertEqual("No associated account", json.loads(r.data)["msg"])

    def test_jwt_add_redirect_with_account_id_on_token_after_login(self):
        """
        Depois do processo de login, o token JWT conterá o account_id da conta padrão
        do usuário.
        """
        test_client = application.test_client()

        with application.app_context(), patch.object(
            routes,
            "check_authentication_successful",
            return_value={"email": self.user.email},
        ), patch.object(routes, "redirect") as redirect_mock:
            test_client.get("/authenticate/google")

            jwt_token = redirect_mock.call_args_list[0][0][0].split("=")[1]
            token_content = jwt.decode(jwt_token, conf.SECRET_KEY)

            self.assertEqual(self.user.email, token_content["user"]["email"])
            self.assertEqual(self.user.name, token_content["user"]["name"])
            self.assertEqual(
                self.account_dev.id, token_content["current_account"]["id"]
            )
            self.assertEqual(
                self.account_dev.name, token_content["current_account"]["name"]
            )
            self.assertEqual(
                self.account_dev.namespace,
                token_content["current_account"]["namespace"],
            )

    def test_add_default_account_on_first_jwt_token(self):
        """
        Depois do processo de login, o token JWT conterá o account_id da conta padrão
        do usuário.
        """
        test_client = application.test_client()
        MagicMock()

        with application.app_context(), patch.object(
            routes,
            "check_authentication_successful",
            return_value={"email": self.user.email},
        ), patch.object(
            routes.jwt_auth, "jwt_encode_callback"
        ) as jwt_auth_mock:
            test_client.get("/authenticate/google")

            user = UserDB(
                tx_name=USER_WITH_MULTIPLE_ACCOUNTS_NAME,
                tx_email=USER_WITH_MULTIPLE_ACCOUNTS_EMAIL,
            )
            jwt_auth_mock.assert_called_once_with(
                jwt_generate_user_info(user, self.account_dev)
            )

    def test_token_return_401_if_user_has_no_associated_account(self):
        with application.test_client() as client:
            r = client.get(
                "/v2/apps",
                headers=self.auth_header(USER_WITH_NO_ACCOUNTS_AUTH_KEY),
            )
            self.assertEqual(401, r.status_code)
            self.assertEqual("No associated account", json.loads(r.data)["msg"])

    def test_jwt_return_401_if_when_account_does_not_exist(self):
        test_client = application.test_client()
        with application.app_context():
            jwt_token = jwt_encode(
                self.user, Account(id=2014, name="", namespace="", owner="")
            )
            auth_header = {
                "Authorization": "JWT {}".format(jwt_token.decode("utf-8"))
            }
            r = test_client.get("/v2/apps", headers=auth_header)
            self.assertEqual(401, r.status_code)
            self.assertEqual(
                "Account does not exist", json.loads(r.data)["msg"]
            )

    def test_token_return_401_if_when_account_does_not_exist(self):
        with application.test_client() as client:
            r = client.get(
                "/v2/apps?account_id=1024",
                headers=self.auth_header(USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY),
            )
            self.assertEqual(401, r.status_code)
            self.assertEqual(
                "Account does not exist", json.loads(r.data)["msg"]
            )
