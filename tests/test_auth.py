from collections import namedtuple

import jwt
import json

from mock import patch, MagicMock
from unittest import TestCase, skip
import unittest
from flask import request
import responses

from hollowman.app import application
from hollowman.models import HollowmanSession, User
from hollowman import conf
from hollowman import decorators
import hollowman.upstream
from hollowman.auth.jwt import jwt_payload_handler
from hollowman import routes

from tests import rebuild_schema
from tests.utils import with_json_fixture


class TestAuthentication(TestCase):

    @with_json_fixture("single_full_app.json")
    def setUp(self, fixture):
        rebuild_schema()
        self.session = HollowmanSession()
        self.session.add(User(tx_email="user@host.com.br", tx_name="John Doe", tx_authkey="69ed620926be4067a36402c3f7e9ddf0"))
        self.session.commit()
        self.response_http_200 = MagicMock(status_code=200)
        responses.add(method='GET',
                         url=conf.MARATHON_ENDPOINT + '/v2/apps',
                         body=json.dumps({'apps': [fixture]}),
                         status=200)
        responses.start()


    def tearDown(self):
        self.session.close()
        responses.stop()

    def test_jwt_disable_auth_if_env_is_present_even_if_invalid_token(self):
        """
        Env temporária para podermos desligar/ligar a autenticação sem
        precisar comitar código.
        """
        with patch.object(hollowman.upstream, 'replay_request', return_value=self.response_http_200) as replay_mock, \
             patch.multiple(decorators, HOLLOWMAN_ENFORCE_AUTH=False), \
             application.app_context(), \
             application.test_client() as test_client:
                jwt_data = jwt_payload_handler({"email": "user@host.com.br"})
                jwt_token = jwt.encode(jwt_data, key="for-sure-the-wrong-key")
                r = test_client.get("/v2/apps", headers={"Authorization": "JWT {}".format(jwt_token)})
                self.assertEqual(200, r.status_code)

    def test_jwt_populate_user_even_if_auth_is_disabled(self):
        """
        We populate the user even if auth is disabled. What's really disabled is auth enforcement.
        """
        with patch.object(hollowman.upstream, 'replay_request', return_value=self.response_http_200) as replay_mock, \
             patch.multiple(decorators, HOLLOWMAN_ENFORCE_AUTH=False), \
             application.app_context(), \
             application.test_client() as test_client:
                jwt_data = jwt_payload_handler({"email": "user@host.com.br"})
                jwt_token = jwt.encode(jwt_data, key=conf.SECRET_KEY)
                auth_header = {
                    "Authorization": "JWT {}".format(jwt_token.decode('utf-8'))
                }
                r = test_client.get("/v2/apps", headers=auth_header)
                self.assertEqual(200, r.status_code)
                self.assertEqual("user@host.com.br", request.user)

    def test_populate_request_user_if_key_is_valid(self):
        """
        Populates request.user if authentication is successful
        """
        with patch.object(hollowman.upstream, 'replay_request', return_value=self.response_http_200) as replay_mock:
            with application.test_client() as client:
                r = client.get("/v2/apps", headers={"Authorization": "Token 69ed620926be4067a36402c3f7e9ddf0"})
                self.assertEqual(200, r.status_code)
                self.assertEqual("user@host.com.br", request.user)

    def test_return_200_if_key_found(self):
        with patch.object(hollowman.upstream, 'replay_request', return_value=self.response_http_200) as replay_mock:
            with application.test_client() as client:
                r = client.get("/v2/apps", headers={"Authorization": " Token 69ed620926be4067a36402c3f7e9ddf0"})
                self.assertEqual(200, r.status_code)

    def test_return_401_if_key_not_found(self):
        with application.test_client() as client:
            r = client.get("/v2/apps", headers={"Authorization": "Token token-not-found"})
            self.assertEqual(401, r.status_code)
            self.assertEqual("Authorization token is invalid", json.loads(r.data)['msg'])

    def test_return_401_if_no_token_present(self):
        with application.test_client() as client:
            r = client.get("/v2/apps")
            self.assertEqual(401, r.status_code)
            self.assertEqual("Authorization token is invalid", json.loads(r.data)['msg'])

    def test_jwt_do_not_trigger_token_auth_if_jwt_token_is_present(self):
        """
        Both auth uses the same header: Authorization. Token Auth should be called if current token is JWT
        """
        with application.test_client() as test_client, \
             application.app_context(), \
             patch.object(decorators, "HollowmanSession") as session_mock:
                r = test_client.get("/v2/apps", headers={"Authorization": "JWT Token"})
                self.assertEqual(0, session_mock.call_count)

    def test_return_200_if_jwt_token_valid(self):
        with patch.object(hollowman.upstream, 'replay_request', return_value=self.response_http_200) as replay_mock:
            test_client = application.test_client()
            with application.app_context():
                jwt_data = jwt_payload_handler({"email": "user@host.com.br"})
                jwt_token = jwt.encode(jwt_data, key=conf.SECRET_KEY)
                auth_header = {
                    "Authorization": "JWT {}".format(jwt_token.decode('utf-8'))
                }
                r = test_client.get("/v2/apps", headers=auth_header)
                self.assertEqual(200, r.status_code)

    def test_populate_request_user_if_jwt_token_is_valid(self):
        with patch.object(hollowman.upstream, 'replay_request', return_value=self.response_http_200) as replay_mock:
            with application.app_context(), application.test_client() as test_client:
                jwt_data = jwt_payload_handler({"email": "user-jwt@host.com.br"})
                jwt_token = jwt.encode(jwt_data, key=conf.SECRET_KEY)
                auth_header = {
                    "Authorization": "JWT {}".format(jwt_token.decode('utf-8'))
                }
                r = test_client.get("/v2/apps", headers=auth_header)
                self.assertEqual(200, r.status_code)
                self.assertEqual("user-jwt@host.com.br", request.user)

    @unittest.skip("Ainda nao temos usuarios validos/ativos/invalidos")
    def test_return_401_if_jwt_token_is_valid_but_user_is_invalid(self):
        """
        User could be inactive or does not exist
        """
        self.fail()

    def test_return_401_if_jwt_token_is_invalid(self):
        with application.app_context(), application.test_client() as test_client:
            jwt_token = jwt.encode({"email": "user@host.com.br"}, key="wrong key")
            auth_header = {
                "Authorization": "JWT {}".format(jwt_token.decode('utf-8'))
            }
            r = test_client.get("/v2/apps", headers=auth_header)
            self.assertEqual(401, r.status_code)
            self.assertEqual("Authorization token is invalid", json.loads(r.data)['msg'])

    def test_return_401_if_jwt_token_not_present(self):
        test_client = application.test_client()
        with application.app_context():
            r = test_client.get("/v2/apps")
            self.assertEqual(401, r.status_code)
            self.assertEqual("Authorization token is invalid", json.loads(r.data)['msg'])

    def test_redirect_with_jwt_token_after_login(self):
        """
        Checks that the JWT Token contains the right data. For now, the user email got from teh OAuth2 Provider
        """
        test_client = application.test_client()
        with application.app_context(), \
             patch.object(routes, "check_authentication_successful", return_value={"email": "email@host.com.br"}):
            r = test_client.get("/authenticate/google")
            self.assertEqual(302, r.status_code)
            jwt_token = r.headers["Location"].split("=")[1]
            self.assertEqual("email@host.com.br", jwt.decode(jwt_token, key=conf.SECRET_KEY)["email"])

    def test_redirect_with_jwt_url_is_formed_with_unicode_jwt(self):
        test_client = application.test_client()
        jwt = MagicMock()

        with application.app_context(), \
             patch.object(routes, "check_authentication_successful",
                          return_value={"email": "email@host.com.br"}),\
             patch.object(routes.jwt_auth, "jwt_encode_callback", return_value=jwt), \
             patch.object(routes, 'redirect') as redirect:
            response = test_client.get("/authenticate/google")

            jwt.decode.assert_called_once_with('utf-8')
            redirect.assert_called_once_with("{}?jwt={}".format(conf.REDIRECT_AFTER_LOGIN, jwt.decode.return_value))
