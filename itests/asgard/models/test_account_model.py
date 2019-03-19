from asgard.models.account import AccountDB, Account
from itests.util import (
    BaseTestCase,
    ACCOUNT_DEV_ID,
    ACCOUNT_DEV_NAME,
    ACCOUNT_DEV_NAMESPACE,
    ACCOUNT_DEV_OWNER,
)


class AccountModelTest(BaseTestCase):
    async def setUp(self):
        await super(AccountModelTest, self).setUp()

    async def test_transform_from_alchemy_object(self):
        async with self.session() as s:
            account_db = (
                await s.query(AccountDB)
                .filter(AccountDB.id == ACCOUNT_DEV_ID)
                .one()
            )
            account = await Account.from_alchemy_obj(account_db)
            self.assertEqual(account.id, ACCOUNT_DEV_ID)
            self.assertEqual(account.name, ACCOUNT_DEV_NAME)
            self.assertEqual(account.namespace, ACCOUNT_DEV_NAMESPACE)
            self.assertEqual(account.owner, ACCOUNT_DEV_OWNER)
