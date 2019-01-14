from aiopg.sa import create_engine
import sqlalchemy


class _EngineWrapper:
    def __init__(self, coro_engine):
        self._coro_engine = coro_engine
        self._connected = False

    async def engine(self):
        if not self._connected:
            self._engine = await self._coro_engine
            self._connected = True
        return self._engine


class Session:
    def __init__(self, engine_wrapper):
        self._engine_wrapper = engine_wrapper

    async def engine(self):
        return await self._engine_wrapper.engine()

    async def connection(self):
        engine = await self._engine_wrapper.engine()
        self.conn = await engine._acquire()
        return AsgardDBConnection(engine, self.conn, session=self)

    async def __aenter__(self):
        return await self.connection()

    async def __aexit__(self, a, b, c):
        engine = await self._engine_wrapper.engine()
        engine.release(self.conn)


class _SessionMaker:
    def __init__(self, dsn, *args, **kwargs):
        self._engine_wrapper = _EngineWrapper(create_engine(dsn=dsn, **kwargs))
        self._connected = False

    def __call__(self):
        return Session(self._engine_wrapper)

    async def engine(self):
        return await self._engine_wrapper.engine()


class AsgardDBConnection:
    def __init__(self, engine, conn, session):
        self.engine = engine
        self.conn = conn
        self.session = session
        self._query = None

    def query(self, *args):
        prepared_query_params = []
        for item in args:
            if type(item) is sqlalchemy.ext.declarative.api.DeclarativeMeta:
                prepared_query_params.append(item.__table__)
            else:
                prepared_query_params.append(item)
        self._query = sqlalchemy.select(prepared_query_params)
        return self

    def filter(self, *args):
        self._query = self._query.where(*args)
        return self

    def join(self, join_clause):
        self._query = self._query.select_from(join_clause)
        return self

    def begin(self):
        return self.conn.begin()

    async def __aiter__(self):
        return await self.execute(self._query)

    async def __aexit__(self, *args, **kwargs):
        return await self.session.__aexit__(*args, **kwargs)

    async def execute(self, *args, **kwargs):
        return await self.conn.execute(*args, **kwargs)

    def release(self):
        self.engine.release(self.conn)

    async def all(self):
        result = await self.execute(self._query)
        return await result.fetchall()

    async def one(self):
        self._query.limit(2)
        result = await self.execute(self._query)
        result_list = list(await result.fetchall())
        if len(result_list) > 1:
            raise sqlalchemy.orm.exc.MultipleResultsFound
        if not len(result_list):
            raise sqlalchemy.orm.exc.MultipleResultsFound
        return result_list[0]
