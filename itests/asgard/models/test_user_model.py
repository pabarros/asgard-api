from asgard.models.user import User, UserDB
from itests.util import (
    BaseTestCase,
    USER_WITH_MULTIPLE_ACCOUNTS_ID,
    USER_WITH_MULTIPLE_ACCOUNTS_EMAIL,
    USER_WITH_MULTIPLE_ACCOUNTS_NAME,
)


class UserModelTest(BaseTestCase):
    async def setUp(self):
        await super(UserModelTest, self).setUp()

    async def test_user_trasnform_from_alchemy_object(self):
        async with self.session() as s:
            account_db = (
                await s.query(UserDB)
                .filter(UserDB.id == USER_WITH_MULTIPLE_ACCOUNTS_ID)
                .one()
            )
            account = await User.from_alchemy_obj(account_db)
            self.assertEqual(account.name, USER_WITH_MULTIPLE_ACCOUNTS_NAME)
            self.assertEqual(account.email, USER_WITH_MULTIPLE_ACCOUNTS_EMAIL)
