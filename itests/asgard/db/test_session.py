import asynctest
import asyncio

from asgard.db import _SessionMaker
from hollowman.models import User, Account, UserHasAccount
from aiopg.sa import create_engine
from itests.util import PgDataMocker
from tests.conf import TEST_PGSQL_DSN
import sqlalchemy


class ManagedAsContextManagerTest(asynctest.TestCase):
    async def setUp(self):
        self.session = _SessionMaker(TEST_PGSQL_DSN)
        self.pg_data_mocker = PgDataMocker(pool=await self.session.engine())
        self.users_fixture = [
            [10, "Novo User", "email@host.com"],
            [20, "John Doe", "john@host.com"],
        ]
        self.pg_data_mocker.add_data(
            User, ["id", "tx_name", "tx_email"], self.users_fixture
        )

        self.pg_data_mocker.add_data(
            Account, ["id", "name", "namespace", "owner"], [[10, "dev", "dev", "dev"]]
        )

        self.pg_data_mocker.add_data(
            UserHasAccount, ["id", "user_id", "account_id"], [[10, 20, 10]]  # John Doe
        )
        await self.pg_data_mocker.create()

    async def tearDown(self):
        await self.pg_data_mocker.drop()

    async def test_rollback_on_exception(self):
        class RollBackException(Exception):
            pass

        try:
            async with self.session() as conn:
                async with conn.begin():
                    insert_query = User.__table__.insert().values(
                        tx_name="Mais um user", tx_email="mais-um-user@host.com"
                    )
                    await conn.execute(insert_query)
                    raise RollBackException()
        except RollBackException as ex:
            async with self.session() as conn:
                result = await conn.query(User).all()
                self.assertEqual(len(list(result)), 2)
        else:
            async with self.session() as conn:
                result = list(await conn.query(User).all())
                self.assertEqual(1, len(result), "Transaction should not be confirmed")
            self.fail("RollBackException not raised")

    async def test_commit_on_success(self):
        async with self.session() as conn:
            insert_query = User.__table__.insert().values(
                tx_name="Outro User", tx_email="outro-user@host.com"
            )
            await conn.execute(insert_query)

        async with self.session() as conn:
            result_0 = await conn.query(User).all()
            result = list(result_0)
            self.assertEqual(len(result), 3)
            self.assertEqual("Novo User", result[0].tx_name)
            self.assertEqual("John Doe", result[1].tx_name)
            self.assertEqual("Outro User", result[2].tx_name)

    async def test_iterate_result_with_async_for(self):
        expected_users_data = []
        async with self.session() as conn:
            async for u in conn.query(User):
                expected_users_data.append([u.id, u.tx_name, u.tx_email])

        self.assertEqual(expected_users_data, self.users_fixture)

    async def test_query_with_model_no_filters_all_fields(self):
        async with self.session() as conn:
            self.assertEqual(2, len(list(await conn.query(User).all())))

    async def test_query_with_model_specific_fields_two_fields(self):
        async with self.session() as conn:
            result = await conn.query(User.tx_name, User.tx_email).all()

            self.assertEqual(2, len(result))
            self.assertEqual("Novo User", result[0].tx_name)
            self.assertEqual("email@host.com", result[0].tx_email)

    async def test_query_with_model_specific_fields_one_field(self):
        async with self.session() as conn:
            result = await conn.query(User.tx_email).all()

            self.assertEqual(2, len(result))
            self.assertEqual("email@host.com", result[0].tx_email)

    async def test_with_model_with_filter(self):
        async with self.session() as conn:
            result = await conn.query(User).filter(User.tx_name == "John Doe").all()

            self.assertEqual(1, len(result))
            self.assertEqual("john@host.com", result[0].tx_email)

    async def test_with_model_with_join(self):
        import sqlalchemy as sa

        async with self.session() as conn:
            # asgard=# select * from enqstwstis."user" as u, enqstwstis.account as a, enqstwstis.user_has_account as ua where u.id = ua.user_id and a.id = ua.account_id;
            # id | tx_name  |   tx_email    | tx_authkey | bl_system | id | name | namespace | owner | id | user_id | account_id
            # ----+----------+---------------+------------+-----------+----+------+-----------+-------+----+---------+------------
            #  2 | John Doe | john@host.com |            | f         |  1 | dev  | dev       | dev   |  1 |       2 |          1
            join = User.__table__.join(
                UserHasAccount, User.id == UserHasAccount.c.user_id
            ).join(Account.__table__, Account.id == UserHasAccount.c.account_id)
            # select = sa.select([User.__table__]).select_from(join)

            # result_raw = list(await conn.execute(select))
            # self.assertEqual(1, len(result_raw))
            # self.assertEqual("John Doe", result_raw[0].tx_name)

            result = await conn.query(User).join(join).all()
            self.assertEqual(1, len(result))
            self.assertEqual("John Doe", result[0].tx_name)

    async def test_must_release_connection_from_pool(self):
        """
        Montamos um pool de 1 conexão mas abrimos duas.
        Se o código estiver correto, segunda query não vai executar pois a unica
        conexão está ocupada com a primeira query.
        """

        SessionClass = _SessionMaker(TEST_PGSQL_DSN, maxsize=1)

        async def coro():
            async with SessionClass() as conn1:
                async with SessionClass() as conn2:
                    pass

        with self.assertRaises(asyncio.TimeoutError):
            await asyncio.wait_for(coro(), 0.5)

    async def test_get_one_OK(self):
        async with self.session() as conn:
            result = await conn.query(User).filter(User.id == 20).one()
            self.assertEqual(20, result.id)

    async def test_get_one_more_than_one_result(self):
        """
        Raises sqlalchemy.orm.exc.MultipleResultsFound
        """
        with self.assertRaises(sqlalchemy.orm.exc.MultipleResultsFound):
            async with self.session() as conn:
                await conn.query(User).one()

    async def test_get_one_no_result_found(self):
        """
        Raises sqlalchemy.orm.exc.NoResultFound
        """
        with self.assertRaises(sqlalchemy.orm.exc.NoResultFound):
            async with self.session() as conn:
                await conn.query(User).filter(User.tx_email == "not-found").one()
