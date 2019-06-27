from asgard.backends.accounts import AccountsBackend
from asgard.models.account import Account
from asgard.models.user import User
from itests.util import (
    BaseTestCase,
    ACCOUNT_DEV_ID,
    ACCOUNT_DEV_DICT,
    ACCOUNT_WITH_NO_USERS_DICT,
    USER_WITH_MULTIPLE_ACCOUNTS_DICT,
    USER_WITH_ONE_ACCOUNT_DICT,
)


class AccountsBackendTest(BaseTestCase):
    async def setUp(self):
        await super(AccountsBackendTest, self).setUp()
        self.backend = AccountsBackend()

    async def tearDown(self):
        await super(AccountsBackendTest, self).tearDown()

    async def test_get_account_by_id_account_not_found(self):
        account = await self.backend.get_account_by_id(8000)
        self.assertIsNone(account)

    async def test_account_by_id_account_exists(self):
        account = await self.backend.get_account_by_id(ACCOUNT_DEV_ID)
        self.assertEqual(Account(**ACCOUNT_DEV_DICT), account)

    async def test_account_list_all_accounts_empty_result(self):
        accounts = await self.backend.get_accounts()
        self.assertEquals(3, len(accounts))

    async def test_accounts_get_users_account_has_users(self):
        account = Account(**ACCOUNT_DEV_DICT)
        users = await self.backend.get_users_from_account(account)
        self.assertEqual(2, len(users))
        self.assertEqual(
            [
                User(**USER_WITH_MULTIPLE_ACCOUNTS_DICT),
                User(**USER_WITH_ONE_ACCOUNT_DICT),
            ],
            users,
        )

    async def test_accounts_get_users_account_does_not_have_any_users(self):
        account = Account(**ACCOUNT_WITH_NO_USERS_DICT)
        users = await self.backend.get_users_from_account(account)
        self.assertEqual(0, len(users))
        self.assertEqual([], users)
