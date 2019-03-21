from asgard.db import AsgardDBSession
from asgard.models.user import User
from itests.util import (
    BaseTestCase,
    USER_WITH_MULTIPLE_ACCOUNTS_ID,
    USER_WITH_MULTIPLE_ACCOUNTS_EMAIL,
    USER_WITH_MULTIPLE_ACCOUNTS_NAME,
    USER_WITH_MULTIPLE_ACCOUNTS_DICT,
)


class UserModelTest(BaseTestCase):
    async def setUp(self):
        await super(UserModelTest, self).setUp()

    async def tearDown(self):
        await super(UserModelTest, self).tearDown()

    async def test_user_trasnform_from_alchemy_object(self):
        user = User(**USER_WITH_MULTIPLE_ACCOUNTS_DICT)
        _, UserDB = await user.to_alchemy_obj()
        async with AsgardDBSession() as s:
            user_db = (
                await s.query(UserDB)
                .filter(UserDB.id == USER_WITH_MULTIPLE_ACCOUNTS_ID)
                .one()
            )
            user = await User.from_alchemy_obj(user_db)
            self.assertEqual(user.name, USER_WITH_MULTIPLE_ACCOUNTS_NAME)
            self.assertEqual(user.email, USER_WITH_MULTIPLE_ACCOUNTS_EMAIL)

    async def test_user_transform_to_alchemy_object(self):
        user = User(**USER_WITH_MULTIPLE_ACCOUNTS_DICT)
        user_db, UserDB = await user.to_alchemy_obj()

        self.assertEqual(user_db.id, USER_WITH_MULTIPLE_ACCOUNTS_ID)
        self.assertEqual(user_db.tx_name, USER_WITH_MULTIPLE_ACCOUNTS_NAME)
        self.assertEqual(user_db.tx_email, USER_WITH_MULTIPLE_ACCOUNTS_EMAIL)
        async with AsgardDBSession() as s:
            result = (
                await s.query(UserDB)
                .filter(UserDB.id == USER_WITH_MULTIPLE_ACCOUNTS_ID)
                .one()
            )
            user_model = await User.from_alchemy_obj(result)
            self.assertEqual(user_model.name, USER_WITH_MULTIPLE_ACCOUNTS_NAME)
            self.assertEqual(
                user_model.email, USER_WITH_MULTIPLE_ACCOUNTS_EMAIL
            )
