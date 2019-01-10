import asyncio
import random
import string
from collections import defaultdict
from typing import Dict, List, Type, Any, Iterable

from aiopg.sa import Engine
from sqlalchemy import Table
from sqlalchemy.sql.ddl import CreateTable, CreateSchema, DropSchema


class PgDataMocker:
    def __init__(self, pool: Engine):
        self.data: Dict[Table, List[Dict]] = defaultdict(list)
        self.pool = pool
        self.schema = ''.join(random.choices(string.ascii_lowercase, k=10))
        self._used_tables = []

    def add_data(self, model: Type, field_names: List[str], data: List[List[Any]]):
        if not data:
            return
        assert all(len(field_names) == len(row) for row in data)

        if type(model) is not Table:
            table = model.__table__
        else:
            table = model

        # ensure schema
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
        commands = (table.insert().values(self.data[table]) for table in self._used_tables)
        async with self.pool.acquire() as conn:
            for command in commands:
                await conn.execute(command)

    async def drop(self):
        async with self.pool.acquire() as conn:
            await conn.execute(DropSchema(self.schema, cascade=True))
