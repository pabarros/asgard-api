import random
import string
from collections import defaultdict
from importlib import reload
from typing import Any, Dict, List, Type, Set

import asyncworker
from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer
from aiopg.sa import Engine
from asynctest import TestCase, mock
from sqlalchemy import Table
from sqlalchemy.sql.ddl import CreateTable
from tests.conf import TEST_PGSQL_DSN

import asgard.db
import hollowman.conf
from asgard.db import _SessionMaker
from hollowman.models import Account, User, UserHasAccount


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


class BaseTestCase(TestCase):
    async def setUp(self):
        with mock.patch.object(
            hollowman.conf, "HOLLOWMAN_DB_URL", TEST_PGSQL_DSN
        ):
            reload(asgard.db)

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
                [10, "Dev Team", "dev", "dev"],
                [11, "Infra Team", "infra", "infra"],
                [12, "Other Team", "other", "other"],
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

    async def tearDown(self):
        await self.pg_data_mocker.drop()

    async def aiohttp_client(self, app: asyncworker.App):
        routes = app.routes_registry.http_routes
        http_app = web.Application()
        for route in routes:
            http_app.router.add_route(**route)
        server = TestServer(http_app)
        client = TestClient(server)
        await server.start_server()

        return client
