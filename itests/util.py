import asyncio
import random
import string
from collections import defaultdict
from typing import Dict, List, Type, Any, Iterable
from asynctest import TestCase
import asyncworker

from aiopg.sa import Engine
from sqlalchemy import Table
from sqlalchemy.sql.ddl import CreateTable, CreateSchema, DropSchema


class PgDataMocker:
    def __init__(self, pool: Engine):
        self.data: Dict[Table, List[Dict]] = defaultdict(list)
        self.pool = pool
        self.schema = "".join(random.choices(string.ascii_lowercase, k=10))
        self._used_tables = []
        self._original_table_schemas = {}

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

        # ensure schema
        self._original_table_schemas[table] = table.schema
        table.schema = self.schema

        self._used_tables.append(table)
        self.data[table].extend((dict(zip(field_names, row)) for row in data))

    async def _create_schema(self):
        async with self.pool.acquire() as conn:
            await conn.execute(CreateSchema(self.schema))
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

    async def drop(self):
        async with self.pool.acquire() as conn:
            await conn.execute(DropSchema(self.schema, cascade=True))
        for table, original_schema in self._original_table_schemas.items():
            table.schema = original_schema


from asyncworker.signals.handlers.http import HTTPServer
from asyncworker import RouteTypes
import asyncio
from aiohttp.test_utils import TestClient, TestServer
from aiohttp import web

from importlib import reload
from asynctest import mock
from tests.conf import TEST_PGSQL_DSN
import hollowman.conf
import asgard.db


class BaseTestCase(TestCase):
    async def setUp(self):
        with mock.patch.object(
            hollowman.conf, "HOLLOWMAN_DB_URL", TEST_PGSQL_DSN
        ):
            reload(asgard.db)

    async def tearDown(self):
        pass

    async def aiohttp_client(self, app: asyncworker.App):
        routes = app.routes_registry.http_routes
        http_app = web.Application()
        for route in routes:
            http_app.router.add_route(**route)
        server = TestServer(http_app)
        client = TestClient(server)
        await server.start_server()

        return client
