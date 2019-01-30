from collections import namedtuple
from importlib import reload

import asgard.db

import jwt
import json
import asyncio

from aiohttp.test_utils import TestClient, TestServer
from aiohttp import web

from mock import patch, MagicMock
from asynctest import TestCase, skip, mock
import os
from hollowman.models import HollowmanSession, User, Account, UserHasAccount
import hollowman.conf
from hollowman.auth.jwt import jwt_auth, jwt_generate_user_info

from asyncworker import App
from asyncworker.options import RouteTypes
from asyncworker.conf import Settings
from asyncworker.signals.handlers.http import HTTPServer

from asgard.db import _SessionMaker
from asgard.http.auth import auth_required
from asgard.http.auth.jwt import jwt_encode

from itests.util import PgDataMocker
from tests.conf import TEST_PGSQL_DSN

from tests import rebuild_schema
from tests.utils import with_json_fixture


class AuthRequiredTest(TestCase):
    async def setUp(self):
        self.app = App("", "", "", 1)

        with mock.patch.dict(os.environ, ASYNCWORKER_HTTP_PORT="9999"):
            self.asyncworker_settings_mock = Settings()

        with mock.patch.object(
            hollowman.conf, "HOLLOWMAN_DB_URL", TEST_PGSQL_DSN
        ):
            reload(asgard.db)

        self.asyncworker_settings_patcher = mock.patch(
            "asyncworker.signals.handlers.http.settings",
            self.asyncworker_settings_mock,
        )
        self.asyncworker_settings_patcher.start()

        self.signal_handler = HTTPServer()

        self.session = _SessionMaker(TEST_PGSQL_DSN)
        self.pg_data_mocker = PgDataMocker(pool=await self.session.engine())
        self.users_fixture = [
            [
                20,
                "John Doe",
                "john@host.com",
                "69ed620926be4067a36402c3f7e9ddf0",
            ],
            [
                21,
                "User with no acounts",
                "user-no-accounts@host.com",
                "7b4184bfe7d2349eb56bcfb9dc246cf8",
            ],
        ]
        self.pg_data_mocker.add_data(
            User,
            ["id", "tx_name", "tx_email", "tx_authkey"],
            self.users_fixture,
        )

        self.pg_data_mocker.add_data(
            Account,
            ["id", "name", "namespace", "owner"],
            [
                [10, "Dev Team", "dev", "company"],
                [11, "Infra Team", "infra", "company"],
                [12, "Other Team", "other", "company"],
            ],
        )

        self.pg_data_mocker.add_data(
            UserHasAccount,
            ["id", "user_id", "account_id"],
            [
                [10, 20, 10],
                [11, 20, 11],
            ],  # John Doe, accounts: Dev Team, Infra Team
        )
        await self.pg_data_mocker.create()

        @self.app.route(["/"], methods=["GET"], type=RouteTypes.HTTP)
        @auth_required
        async def handler(r):
            auth_user = r["user"]
            data = {
                "user": auth_user.tx_email,
                "current_account": {
                    "id": auth_user.current_account.id,
                    "namespace": auth_user.current_account.namespace,
                    "name": auth_user.current_account.name,
                },
            }
            return web.json_response(data)

    async def tearDown(self):
        mock.patch.stopall()
        await self.signal_handler.shutdown(self.app)

    async def test_auth_token_populate_request_user_if_key_is_valid(self):
        """
        Populates request.user if authentication is successful
        """

        await self.signal_handler.startup(self.app)

        async with TestClient(
            TestServer(self.app[RouteTypes.HTTP]["app"]),
            loop=asyncio.get_event_loop(),
        ) as client:
            resp = await client.get(
                "/",
                headers={
                    "Authorization": "Token 69ed620926be4067a36402c3f7e9ddf0"
                },
            )
            data = await resp.json()
            self.assertEqual(200, resp.status)
            self.assertEqual("john@host.com", data["user"])

    async def test_auth_auth_fails_if_token_type_is_invalid(self):

        await self.signal_handler.startup(self.app)

        async with TestClient(
            TestServer(self.app[RouteTypes.HTTP]["app"]),
            loop=asyncio.get_event_loop(),
        ) as client:
            resp = await client.get(
                "/", headers={"Authorization": "Invalid-Type invalidToken"}
            )
            data = await resp.json()
            self.assertEqual(401, resp.status)
            self.assertEqual({"msg": "Authorization token is invalid"}, data)

    async def test_auth_auth_fails_if_header_is_not_present(self):

        await self.signal_handler.startup(self.app)

        async with TestClient(
            TestServer(self.app[RouteTypes.HTTP]["app"]),
            loop=asyncio.get_event_loop(),
        ) as client:
            resp = await client.get("/")
            data = await resp.json()
            self.assertEqual(401, resp.status)
            self.assertEqual({"msg": "Authorization token is invalid"}, data)

    async def test_auth_auth_failts_if_key_not_found(self):
        await self.signal_handler.startup(self.app)
        async with TestClient(
            TestServer(self.app[RouteTypes.HTTP]["app"]),
            loop=asyncio.get_event_loop(),
        ) as client:
            resp = await client.get(
                "/", headers={"Authorization": "Token token-not-found"}
            )
            data = await resp.json()
            self.assertEqual(401, resp.status)
            self.assertEqual({"msg": "Authorization token is invalid"}, data)

    async def test_auth_auth_fails_if_user_has_no_associated_account(self):
        await self.signal_handler.startup(self.app)
        async with TestClient(
            TestServer(self.app[RouteTypes.HTTP]["app"]),
            loop=asyncio.get_event_loop(),
        ) as client:
            resp = await client.get(
                "/",
                headers={
                    "Authorization": "Token 7b4184bfe7d2349eb56bcfb9dc246cf8"
                },
            )
            data = await resp.json()
            self.assertEqual(401, resp.status)
            self.assertEqual({"msg": "No associated account"}, data)

    async def test_auth_auth_fails_if_desired_account_does_not_exist(self):
        await self.signal_handler.startup(self.app)
        async with TestClient(
            TestServer(self.app[RouteTypes.HTTP]["app"]),
            loop=asyncio.get_event_loop(),
        ) as client:
            resp = await client.get(
                "/",
                params={"account_id": 42},
                headers={
                    "Authorization": "Token 69ed620926be4067a36402c3f7e9ddf0"
                },
            )
            data = await resp.json()
            self.assertEqual(401, resp.status)
            self.assertEqual({"msg": "Account does not exist"}, data)

    async def test_auth_populate_default_account_if_request_account_is_empty(
        self
    ):
        await self.signal_handler.startup(self.app)
        async with TestClient(
            TestServer(self.app[RouteTypes.HTTP]["app"]),
            loop=asyncio.get_event_loop(),
        ) as client:
            resp = await client.get(
                "/",
                headers={
                    "Authorization": "Token 69ed620926be4067a36402c3f7e9ddf0"
                },
            )
            data = await resp.json()
            self.assertEqual(200, resp.status)
            self.assertEqual(
                {
                    "user": "john@host.com",
                    "current_account": {
                        "name": "Dev Team",
                        "id": 10,
                        "namespace": "dev",
                    },
                },
                data,
            )

    async def test_auth_auth_fails_if_user_is_not_associated_to_desired_account(
        self
    ):
        """
        Qualquer request com `?account_id` que o usuário nao esteja vinculado, retorna 401
        """
        await self.signal_handler.startup(self.app)
        async with TestClient(
            TestServer(self.app[RouteTypes.HTTP]["app"]),
            loop=asyncio.get_event_loop(),
        ) as client:
            resp = await client.get(
                "/",
                params={"account_id": 12},  # Other Account
                headers={
                    "Authorization": "Token 69ed620926be4067a36402c3f7e9ddf0"
                },
            )
            data = await resp.json()
            self.assertEqual(401, resp.status)
            self.assertEqual(
                {"msg": "Permission Denied to access this account"}, data
            )

    @skip("Ainda nao temos usuarios validos/ativos/invalidos")
    def test_auth_auth_failts_if_token_is_valid_but_user_is_invalid(self):
        """
        User could be inactive or does not exist
        """
        self.fail()

    @skip("Ainda nao temos usuarios validos/ativos/invalidos")
    def test_jwt_auth_failts_if_token_is_valid_but_user_is_invalid(self):
        """
        User could be inactive or does not exist
        """
        self.fail()

    async def test_jwt_token_populate_request_user_if_key_is_valid(self):
        """
        Populates request.user if authentication is successful
        """

        await self.signal_handler.startup(self.app)

        jwt_token = jwt_encode({"user": {"email": "john@host.com"}})
        auth_header = {
            "Authorization": "JWT {}".format(jwt_token.decode("utf-8"))
        }

        async with TestClient(
            TestServer(self.app[RouteTypes.HTTP]["app"]),
            loop=asyncio.get_event_loop(),
        ) as client:
            resp = await client.get("/", headers=auth_header)
            data = await resp.json()
            self.assertEqual(200, resp.status)
            self.assertEqual("john@host.com", data["user"])

    async def test_jwt_auth_fails_if_jwt_token_is_invalid(self):
        await self.signal_handler.startup(self.app)

        jwt_token = jwt.encode({"email": "user@host.com.br"}, key="wrong key")
        auth_header = {
            "Authorization": "JWT {}".format(jwt_token.decode("utf-8"))
        }

        async with TestClient(
            TestServer(self.app[RouteTypes.HTTP]["app"]),
            loop=asyncio.get_event_loop(),
        ) as client:
            resp = await client.get("/", headers=auth_header)
            data = await resp.json()
            self.assertEqual(401, resp.status)
            self.assertEqual({"msg": "Authorization token is invalid"}, data)
