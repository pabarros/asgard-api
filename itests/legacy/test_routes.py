from flask import Response
from mock import patch

import hollowman.routes
from asgard.models.account import AccountDB
from asgard.models.user import UserDB
from hollowman.app import application
from itests.util import (
    BaseTestCase,
    ACCOUNT_DEV_ID,
    ACCOUNT_DEV_NAME,
    ACCOUNT_DEV_NAMESPACE,
    ACCOUNT_DEV_OWNER,
)


class RoutesTest(BaseTestCase):
    async def setUp(self):
        await super(RoutesTest, self).setUp()
        self.user = UserDB()
        self.account_dev = AccountDB(
            id=ACCOUNT_DEV_ID,
            name=ACCOUNT_DEV_NAME,
            namespace=ACCOUNT_DEV_NAMESPACE,
            owner=ACCOUNT_DEV_OWNER,
        )
        self.user.accounts = [self.account_dev]

        self.proxy_mock_patcher = patch.object(hollowman.routes, "raw_proxy")
        self.proxy_mock = self.proxy_mock_patcher.start()
        self.proxy_mock.return_value = Response(status=200)

    async def tearDown(self):
        await super(RoutesTest, self).tearDown()
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
