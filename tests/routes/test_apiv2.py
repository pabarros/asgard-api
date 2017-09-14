from typing import Dict

import jwt

from unittest import TestCase
from unittest.mock import patch

from flask import Response

from hollowman.app import application
from hollowman import conf
from hollowman.auth.jwt import jwt_payload_handler
from tests import rebuild_schema

from hollowman.models import HollowmanSession, User


class TestAuthentication(TestCase):
    def setUp(self):
        rebuild_schema()
        self.session = HollowmanSession()

        self.new_dispatcher_user = User(
            tx_email="xablau@host.com.br",
            tx_name="Xablau",
            tx_authkey="69ed620926be4067a36402c3f7e9ddf0")
        self.normal_user = User(
            tx_email="user@host.com.br",
            tx_name="John Doe",
            tx_authkey="70ed620926be4067a36402c3f7e9ddf0")
        self.session.add_all([self.new_dispatcher_user, self.normal_user])
        self.session.commit()

        self.response_http_200 = Response(status=200)

        self.conf_patch = patch.object(conf, 'HOLLOWMAN_NEW_DISPATCHER_USERS',
                                       [self.new_dispatcher_user.tx_email])
        self.conf_patch.start()

    def tearDown(self):
        patch.stopall()

    def make_auth_header(self, email: str) -> Dict[str, str]:
        jwt_data = jwt_payload_handler({"email": email})
        jwt_token = jwt.encode(jwt_data, key=conf.SECRET_KEY)
        return {
            "Authorization": "JWT {}".format(jwt_token.decode('utf-8'))
        }

    def test_it_calls_the_new_filters_dispatching_for_configured_users(self):
        with patch('hollowman.routes.request_handlers') as request_handlers:
            test_client = application.test_client()
            with application.app_context():
                auth_header = self.make_auth_header(self.new_dispatcher_user.tx_email)

                request_handlers.new.return_value = self.response_http_200
                r = test_client.get("/v2/apps", headers=auth_header)
                self.assertEqual(200, r.status_code)

                request_handlers.new.assert_called_once()
                request_handlers.old.assert_not_called()

    def test_it_calls_the_old_filters_dispatching_for_other_users(self):
        with patch('hollowman.routes.request_handlers') as request_handlers:
            test_client = application.test_client()
            with application.app_context():
                auth_header = self.make_auth_header(self.normal_user.tx_email)

                request_handlers.old.return_value = self.response_http_200
                r = test_client.get("/v2/apps", headers=auth_header)
                self.assertEqual(200, r.status_code)

                request_handlers.new.assert_not_called()
                request_handlers.old.assert_called_once()
