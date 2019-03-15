from asgard.api import users
from asgard.app import app
from asgard.http.auth.jwt import jwt_encode
from itests.util import (
    BaseTestCase,
    USER_WITH_NO_ACCOUNTS_AUTH_KEY,
    USER_WITH_MULTIPLE_ACCOUNTS_NAME,
    USER_WITH_MULTIPLE_ACCOUNTS_EMAIL,
    ACCOUNT_DEV_ID,
    ACCOUNT_DEV_NAME,
)


class UsersTestCase(BaseTestCase):
    async def setUp(self):
        await super(UsersTestCase, self).setUp()
        self.client = await self.aiohttp_client(app)

    async def tearDown(self):
        await super(UsersTestCase, self).tearDown()

    async def test_returns_user_basic_info(self):

        resp = await self.client.get(
            "/users/me",
            headers={
                "Authorization": f"Token {USER_WITH_NO_ACCOUNTS_AUTH_KEY}"
            },
        )
        self.assertEqual(401, resp.status)

    async def test_users_me_invalid_token(self):

        resp = await self.client.get(
            "/users/me", headers={"Authorization": f"Token Invalid-Token"}
        )
        self.assertEqual(401, resp.status)

    async def test_jwt_me_returns_user_info_with_alternate_accounts(self):
        """
        Conferir que a lista de contas alternativas, *não inclui* a conta atual,
        que está no token JWT
        """
        jwt_token = jwt_encode(
            {
                "user": {
                    "nome": USER_WITH_MULTIPLE_ACCOUNTS_NAME,
                    "email": USER_WITH_MULTIPLE_ACCOUNTS_EMAIL,
                },
                "current_account": {
                    "id": ACCOUNT_DEV_ID,
                    "name": ACCOUNT_DEV_NAME,
                },
            }
        )
        resp = await self.client.get(
            "/users/me",
            headers={"Authorization": f"JWT {jwt_token.decode('utf-8')}"},
        )
        self.assertEqual(200, resp.status)
        data = await resp.json()
        self.assertDictEqual(
            {
                "name": USER_WITH_MULTIPLE_ACCOUNTS_NAME,
                "email": USER_WITH_MULTIPLE_ACCOUNTS_EMAIL,
                "current_account": {
                    "id": ACCOUNT_DEV_ID,
                    "name": ACCOUNT_DEV_NAME,
                },
                "accounts": [{"id": 11, "name": "Infra Team"}],
            },
            data,
        )

    async def test_returns_user_info_no_permission_for_chosen_account(self):
        """
        Se fazemos um request GET /users/me?account_id=3
        mas o usuário não tem permissão para acessar a conta escolhida,
        devemos retornar HTTP 403
        """
        self.fail()
