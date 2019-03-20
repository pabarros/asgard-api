import random
import string
from collections import defaultdict
from importlib import reload
from typing import Any, Dict, List, Type, Set

import asyncworker
from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer
from aiopg.sa import Engine
from asynctest import TestCase
from sqlalchemy import Table
from sqlalchemy.sql.ddl import CreateTable

import asgard.backends.users
import asgard.db
from asgard.conf import settings
from asgard.db import _SessionMaker
from asgard.models.account import AccountDB as Account
from asgard.models.user import UserDB as User
from asgard.models.user_has_account import UserHasAccount


class PgDataMocker:
    def __init__(self, pool: Engine) -> None:
        self.data: Dict[Table, List[Dict]] = defaultdict(list)
        self.pool = pool
        self.schema = "".join(random.choices(string.ascii_lowercase, k=10))
        self._used_tables: List[Table] = []
        self._table_names: Set[str] = set()
        self._original_table_schemas: Dict[Table, str] = {}

    def add_data(
        self, model: Type, field_names: List[str], data: List[List[Any]]
    ):
        if not data:
            return
        assert all(len(field_names) == len(row) for row in data)

        if type(model) is not Table:
            table = model.__table__
        else:
            table = model

        if table.name not in self._table_names:
            # ensure schema
            self._original_table_schemas[table] = table.schema
            table.schema = self.schema
            self._used_tables.append(table)

        self.data[table].extend((dict(zip(field_names, row)) for row in data))
        self._table_names.add(table.name)

    async def _create_schema(self):
        await self._drop_schema_only()
        async with self.pool.acquire() as conn:
            await conn.execute(f"CREATE SCHEMA IF NOT EXISTS {self.schema}")
            for table in self._used_tables:
                await conn.execute(CreateTable(table))

    async def create(self):
        await self._create_schema()
        commands = (
            table.insert().values(self.data[table])
            for table in self._used_tables
        )
        async with self.pool.acquire() as conn:
            for command in commands:
                await conn.execute(command)

    async def _drop_schema_only(self):
        async with self.pool.acquire() as conn:
            await conn.execute(f"DROP SCHEMA IF EXISTS {self.schema} CASCADE")

    async def drop(self):
        await self._drop_schema_only()
        for table, original_schema in self._original_table_schemas.items():
            table.schema = original_schema


ACCOUNT_INFRA_NAME: str = "Infra Team"
ACCOUNT_INFRA_ID: int = 11
ACCOUNT_INFRA_NAMESPACE: str = "infra"
ACCOUNT_INFRA_OWNER: str = "infra"


ACCOUNT_INFRA_DICT = {
    "id": ACCOUNT_INFRA_ID,
    "name": ACCOUNT_INFRA_NAME,
    "namespace": ACCOUNT_INFRA_NAMESPACE,
    "owner": ACCOUNT_INFRA_OWNER,
}

ACCOUNT_DEV_NAME: str = "Dev Team"
ACCOUNT_DEV_ID: int = 10
ACCOUNT_DEV_NAMESPACE: str = "dev"
ACCOUNT_DEV_OWNER: str = "dev"

ACCOUNT_DEV_DICT = {
    "id": ACCOUNT_DEV_ID,
    "name": ACCOUNT_DEV_NAME,
    "namespace": ACCOUNT_DEV_NAMESPACE,
    "owner": ACCOUNT_DEV_OWNER,
}

USER_WITH_ONE_ACCOUNT_ID = 22
USER_WITH_ONE_ACCOUNT_AUTH_KEY = ""
USER_WITH_ONE_ACCOUNT_NAME = "User one account"
USER_WITH_ONE_ACCOUNT_EMAIL = "userone@server.com"

USER_WITH_ONE_ACCOUNT_DICT = {
    "id": USER_WITH_ONE_ACCOUNT_ID,
    "name": USER_WITH_ONE_ACCOUNT_NAME,
    "email": USER_WITH_ONE_ACCOUNT_EMAIL,
}

USER_WITH_NO_ACCOUNTS_ID = 21
USER_WITH_NO_ACCOUNTS_AUTH_KEY = "7b4184bfe7d2349eb56bcfb9dc246cf8"
USER_WITH_NO_ACCOUNTS_NAME = "User with no acounts"
USER_WITH_NO_ACCOUNTS_EMAIL = "user-no-accounts@host.com"

USER_WITH_MULTIPLE_ACCOUNTS_ID = 20
USER_WITH_MULTIPLE_ACCOUNTS_EMAIL = "john@host.com"
USER_WITH_MULTIPLE_ACCOUNTS_NAME = "John Doe"
USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY = "69ed620926be4067a36402c3f7e9ddf0"


USER_WITH_MULTIPLE_ACCOUNTS_DICT = {
    "id": USER_WITH_MULTIPLE_ACCOUNTS_ID,
    "name": USER_WITH_MULTIPLE_ACCOUNTS_NAME,
    "email": USER_WITH_MULTIPLE_ACCOUNTS_EMAIL,
}


class BaseTestCase(TestCase):
    async def setUp(self):
        reload(asgard.db)
        reload(asgard.backends.users)

        self.session = _SessionMaker(settings.DB_URL)
        self.pg_data_mocker = PgDataMocker(pool=await self.session.engine())
        self.users_fixture = [
            [
                USER_WITH_MULTIPLE_ACCOUNTS_ID,
                USER_WITH_MULTIPLE_ACCOUNTS_NAME,
                USER_WITH_MULTIPLE_ACCOUNTS_EMAIL,
                USER_WITH_MULTIPLE_ACCOUNTS_AUTH_KEY,
            ],
            [
                USER_WITH_NO_ACCOUNTS_ID,
                USER_WITH_NO_ACCOUNTS_NAME,
                USER_WITH_NO_ACCOUNTS_EMAIL,
                USER_WITH_NO_ACCOUNTS_AUTH_KEY,
            ],
            [
                USER_WITH_ONE_ACCOUNT_ID,
                USER_WITH_ONE_ACCOUNT_NAME,
                USER_WITH_ONE_ACCOUNT_EMAIL,
                USER_WITH_ONE_ACCOUNT_AUTH_KEY,
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
                [
                    ACCOUNT_DEV_ID,
                    ACCOUNT_DEV_NAME,
                    ACCOUNT_DEV_NAMESPACE,
                    ACCOUNT_DEV_OWNER,
                ],
                [
                    ACCOUNT_INFRA_ID,
                    ACCOUNT_INFRA_NAME,
                    ACCOUNT_INFRA_NAMESPACE,
                    ACCOUNT_INFRA_OWNER,
                ],
                [12, "Other Team", "other", "other"],
            ],
        )

        self.pg_data_mocker.add_data(
            UserHasAccount,
            ["id", "user_id", "account_id"],
            [
                [10, USER_WITH_MULTIPLE_ACCOUNTS_ID, ACCOUNT_DEV_ID],
                [11, USER_WITH_MULTIPLE_ACCOUNTS_ID, ACCOUNT_INFRA_ID],
                [12, USER_WITH_ONE_ACCOUNT_ID, ACCOUNT_DEV_ID],
            ],  # John Doe, accounts: Dev Team, Infra Team
        )
        await self.pg_data_mocker.create()

    async def tearDown(self):
        await self.pg_data_mocker.drop()

    async def aiohttp_client(self, app: asyncworker.App) -> TestClient:
        routes = app.routes_registry.http_routes
        http_app = web.Application()
        for route in routes:
            http_app.router.add_route(**route)
        server = TestServer(http_app)
        client = TestClient(server)
        await server.start_server()

        return client
