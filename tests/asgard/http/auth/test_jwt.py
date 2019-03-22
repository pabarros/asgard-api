import jwt
from asynctest import TestCase

from asgard.http.auth.jwt import jwt_encode
from asgard.models.account import Account
from asgard.models.user import User
from hollowman.conf import SECRET_KEY
from itests.util import USER_WITH_ONE_ACCOUNT_DICT, ACCOUNT_DEV_DICT


class JWTTest(TestCase):
    async def test_encode_new_token(self):
        """
        Dado um objeto User e um Account, retorna um novo
        token JWT contendo as informações necessárias
        """

        user = User(**USER_WITH_ONE_ACCOUNT_DICT)
        account = Account(**ACCOUNT_DEV_DICT)
        token = jwt_encode(user, account)

        decoded_token = jwt.decode(token, key=SECRET_KEY)
        self.assertDictEqual(user.dict(), decoded_token["user"])
        self.assertDictEqual(account.dict(), decoded_token["current_account"])
