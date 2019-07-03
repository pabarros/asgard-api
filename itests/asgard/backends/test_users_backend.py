import asgard.services.users
from asgard.backends.users import UsersBackend
from asgard.exceptions import DuplicateEntity
from asgard.models.account import Account
from asgard.models.user import User
from itests.util import (
    BaseTestCase,
    USER_WITH_MULTIPLE_ACCOUNTS_DICT,
    USER_WITH_ONE_ACCOUNT_DICT,
    USER_WITH_NO_ACCOUNTS_DICT,
    USER_WITH_ONE_ACCOUNT_ID,
    USER_WITH_NO_ACCOUNTS_EMAIL,
    ACCOUNT_DEV_DICT,
    ACCOUNT_INFRA_DICT,
)


class UsersBackendTest(BaseTestCase):
    async def setUp(self):
        await super(UsersBackendTest, self).setUp()
        self.backend = UsersBackend()

    async def tearDown(self):
        await super(UsersBackendTest, self).tearDown()

    async def test_get_alternate_accounts_for_user(self):
        user = User(**USER_WITH_MULTIPLE_ACCOUNTS_DICT)
        current_account = Account(**ACCOUNT_DEV_DICT)
        accounts = await UsersBackend().get_alternate_accounts(
            user, current_account
        )
        self.assertEqual(1, len(accounts))
        self.assertEqual([Account(**ACCOUNT_INFRA_DICT)], accounts)

    async def test_get_alternate_accounts_user_has_only_one_account(self):
        """
        Quando um user tem acesso a apenas uma conta, esse método deve retornar uma lista vazia
        """
        user = User(**USER_WITH_ONE_ACCOUNT_DICT)
        current_account = Account(**ACCOUNT_DEV_DICT)
        accounts = await UsersBackend().get_alternate_accounts(
            user, current_account
        )
        self.assertEqual(0, len(accounts))
        self.assertEqual([], accounts)

    async def test_get_user_by_id_user_exists(self):
        user = await self.backend.get_user_by_id(USER_WITH_ONE_ACCOUNT_ID)
        self.assertIsNotNone(user)
        self.assertEqual(User(**USER_WITH_ONE_ACCOUNT_DICT), user)

    async def test_get_user_by_id_user_not_found(self):
        user = await self.backend.get_user_by_id(99)
        self.assertIsNone(user)

    async def test_get_all_users(self):
        users = await self.backend.get_users()
        self.assertCountEqual(
            [
                User(**USER_WITH_MULTIPLE_ACCOUNTS_DICT),
                User(**USER_WITH_ONE_ACCOUNT_DICT),
                User(**USER_WITH_NO_ACCOUNTS_DICT),
            ],
            users,
        )

    async def test_create_user_OK(self):
        user_name = "New User"
        user_email = "newuser@server.com"
        user_created = await self.backend.create_user(
            User(name=user_name, email=user_email)
        )
        self.assertEqual(
            user_created, User(id=1, name=user_name, email=user_email)
        )

    async def test_create_user_duplicate_email(self):
        user_name = "New User"
        user_email = USER_WITH_NO_ACCOUNTS_EMAIL
        with self.assertRaises(DuplicateEntity):
            await self.backend.create_user(
                User(name=user_name, email=user_email)
            )
