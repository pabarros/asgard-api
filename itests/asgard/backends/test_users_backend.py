from importlib import reload

import asgard.services.users
from asgard.backends.users import UsersBackend
from asgard.models.account import Account
from asgard.models.user import User
from asgard.services.users import UsersService
from itests.util import (
    BaseTestCase,
    USER_WITH_MULTIPLE_ACCOUNTS_DICT,
    USER_WITH_ONE_ACCOUNT_DICT,
    ACCOUNT_DEV_DICT,
    ACCOUNT_INFRA_DICT,
)


class UsersBackendTest(BaseTestCase):
    async def setUp(self):
        await super(UsersBackendTest, self).setUp()
        reload(asgard.services.users)

    async def test_get_alternate_accounts_for_user(self):
        user = User(**USER_WITH_MULTIPLE_ACCOUNTS_DICT)
        current_account = Account(**ACCOUNT_DEV_DICT)
        accounts = await UsersService.get_alternate_accounts(
            user, current_account, UsersBackend()
        )
        self.assertEqual(1, len(accounts))
        self.assertEqual([Account(**ACCOUNT_INFRA_DICT)], accounts)

    async def test_get_alternate_accounts_user_has_only_one_account(self):
        """
        Quando um user tem acesso a apenas uma conta, esse método deve retornar uma lista vazia
        """
        user = User(**USER_WITH_ONE_ACCOUNT_DICT)
        current_account = Account(**ACCOUNT_DEV_DICT)
        accounts = await UsersService.get_alternate_accounts(
            user, current_account, UsersBackend()
        )
        self.assertEqual(0, len(accounts))
        self.assertEqual([], accounts)
