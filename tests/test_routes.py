import unittest
from mock import patch
from flask import Response

import hollowman.routes
from hollowman.app import application
from hollowman import decorators
from hollowman.models import User, Account, HollowmanSession

from tests import rebuild_schema


class RoutesTest(unittest.TestCase):
    def setUp(self):
        rebuild_schema()
        self.session = HollowmanSession()
        self.user = User(
            tx_email="user@host.com.br",
            tx_name="John Doe",
            tx_authkey="69ed620926be4067a36402c3f7e9ddf0",
        )
        self.account_dev = Account(
            id=4, name="Dev Team", namespace="dev", owner="company"
        )
        self.user.accounts = [self.account_dev]
        self.session.add(self.account_dev)
        self.session.add(self.user)
        self.session.commit()

        self.proxy_mock_patcher = patch.object(hollowman.routes, "raw_proxy")
        self.proxy_mock = self.proxy_mock_patcher.start()
        self.proxy_mock.return_value = Response(status=200)

    def tearDown(self):
        self.session.close()
        self.proxy_mock_patcher.stop()

    def test_v2_artifacts(self):
        with application.test_client() as client:
            client.get(
                "/v2/artifacts",
                headers={
                    "Authorization": "Token 69ed620926be4067a36402c3f7e9ddf0"
                },
            )

            client.get(
                "/v2/artifacts/etc/hosts",
                headers={
                    "Authorization": "Token 69ed620926be4067a36402c3f7e9ddf0"
                },
            )
            client.put(
                "/v2/artifacts/etc/hosts",
                headers={
                    "Authorization": "Token 69ed620926be4067a36402c3f7e9ddf0"
                },
            )
            client.post(
                "/v2/artifacts/etc/hosts",
                headers={
                    "Authorization": "Token 69ed620926be4067a36402c3f7e9ddf0"
                },
            )
            client.delete(
                "/v2/artifacts/etc/hosts",
                headers={
                    "Authorization": "Token 69ed620926be4067a36402c3f7e9ddf0"
                },
            )

            client.get(
                "/v2/artifacts//etc/hosts",
                headers={
                    "Authorization": "Token 69ed620926be4067a36402c3f7e9ddf0"
                },
            )
            client.put(
                "/v2/artifacts//etc/hosts",
                headers={
                    "Authorization": "Token 69ed620926be4067a36402c3f7e9ddf0"
                },
            )
            client.post(
                "/v2/artifacts//etc/hosts",
                headers={
                    "Authorization": "Token 69ed620926be4067a36402c3f7e9ddf0"
                },
            )
            client.delete(
                "/v2/artifacts//etc/hosts",
                headers={
                    "Authorization": "Token 69ed620926be4067a36402c3f7e9ddf0"
                },
            )
        self.assertEqual(9, self.proxy_mock.call_count)

    def test_v2_info(self):
        with application.test_client() as client:
            client.get(
                "/v2/info",
                headers={
                    "Authorization": "Token 69ed620926be4067a36402c3f7e9ddf0"
                },
            )
            self.assertEqual(1, self.proxy_mock.call_count)

    def test_v2_leader(self):
        with application.test_client() as client:
            client.get(
                "/v2/leader",
                headers={
                    "Authorization": "Token 69ed620926be4067a36402c3f7e9ddf0"
                },
            )
            client.delete(
                "/v2/leader",
                headers={
                    "Authorization": "Token 69ed620926be4067a36402c3f7e9ddf0"
                },
            )
            self.assertEqual(2, self.proxy_mock.call_count)

    def test_v2_info(self):
        with application.test_client() as client:
            client.get(
                "/v2/info",
                headers={
                    "Authorization": "Token 69ed620926be4067a36402c3f7e9ddf0"
                },
            )
            self.assertEqual(1, self.proxy_mock.call_count)

    def test_ping(self):
        with application.test_client() as client:
            client.get(
                "/ping",
                headers={
                    "Authorization": "Token 69ed620926be4067a36402c3f7e9ddf0"
                },
            )
            self.assertEqual(1, self.proxy_mock.call_count)

    def test_metrics(self):
        with application.test_client() as client:
            client.get(
                "/metrics",
                headers={
                    "Authorization": "Token 69ed620926be4067a36402c3f7e9ddf0"
                },
            )
            self.assertEqual(1, self.proxy_mock.call_count)
