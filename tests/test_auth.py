
from collections import namedtuple

import jwt
import json

from mock import patch, MagicMock
from unittest import TestCase, skip
import unittest
from flask import request

from hollowman.app import application
from hollowman.models import HollowmanSession, User
from hollowman import conf
import hollowman.upstream
from hollowman.auth.jwt import jwt_payload_handler

from . import rebuild_schema


class TestAuthentication(TestCase):

    def setUp(self):
        rebuild_schema()
        self.session = HollowmanSession()
        self.session.add(User(tx_email="user@host.com.br", tx_name="John Doe", tx_authkey="69ed620926be4067a36402c3f7e9ddf0"))
        self.session.commit()

    def tearDown(self):
        self.session.close()

    def test_disable_auth_if_env_is_present(self):
        """
        Env temporária para podermo desligar/ligar a autenticação sem
        precisar comitar código.
        """
        self.fail()

    def test_populate_request_user_if_key_is_valid(self):
        """
        Populates request.user if authentication is successful
        """
        response_mock = MagicMock()
        response_mock.status_code = 200
        with patch.object(hollowman.upstream, 'replay_request', return_value=response_mock) as replay_mock:
            with application.test_client() as client:
                r = client.get("/v2/apps", headers={"Authorization": "Token 69ed620926be4067a36402c3f7e9ddf0"})
                self.assertEqual(200, r.status_code)
                self.assertEqual("user@host.com.br", request.user)

    def test_return_200_if_key_found(self):
        response_mock = MagicMock()
        response_mock.status_code = 200
        with patch.object(hollowman.upstream, 'replay_request', return_value=response_mock) as replay_mock:
            with application.test_client() as client:
                r = client.get("/v2/apps", headers={"Authorization": "Token 69ed620926be4067a36402c3f7e9ddf0"})
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

    def test_return_200_if_jwt_token_valid(self):
        response_mock = MagicMock()
        response_mock.status_code = 200
        with patch.object(hollowman.upstream, 'replay_request', return_value=response_mock) as replay_mock:
            test_client = application.test_client()
            with application.app_context():
                jwt_data = jwt_payload_handler({"email": "user@host.com.br"})
                jwt_token = jwt.encode(jwt_data, key=conf.SECRET_KEY)
                r = test_client.get("/v2/apps", headers={"Authorization": "JWT {}".format(jwt_token)})
                self.assertEqual(200, r.status_code)

    def test_populate_request_user_if_jwt_token_is_valid(self):
        response_mock = MagicMock()
        response_mock.status_code = 200
        with patch.object(hollowman.upstream, 'replay_request', return_value=response_mock) as replay_mock:
            with application.app_context(), application.test_client() as test_client:
                jwt_data = jwt_payload_handler({"email": "user-jwt@host.com.br"})
                jwt_token = jwt.encode(jwt_data, key=conf.SECRET_KEY)
                r = test_client.get("/v2/apps", headers={"Authorization": "JWT {}".format(jwt_token)})
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
            r = test_client.get("/v2/apps", headers={"Authorization": "JWT {}".format(jwt_token)})
            self.assertEqual(401, r.status_code)
            self.assertEqual("Authorization token is invalid", json.loads(r.data)['msg'])

    def test_return_401_if_jwt_token_not_present(self):
        test_client = application.test_client()
        with application.app_context():
            r = test_client.get("/v2/apps")
            self.assertEqual(401, r.status_code)
            self.assertEqual("Authorization token is invalid", json.loads(r.data)['msg'])

