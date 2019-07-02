from asynctest import TestCase
from asynctest.mock import CoroutineMock

from asgard.services.users import UsersService


class UsersServiceTest(TestCase):
    async def setUp(self):
        self.service = UsersService()

    async def test_calls_get_alternate_accounts(self):
        backend = CoroutineMock(get_alternate_accounts=CoroutineMock())
        user = CoroutineMock()
        current_account = CoroutineMock()
        await UsersService.get_alternate_accounts(
            user, current_account, backend
        )
        backend.get_alternate_accounts.assert_awaited_with(
            user, current_account
        )

    async def test_calls_backend_get_user_by_id(self):
        backend = CoroutineMock(get_user_by_id=CoroutineMock())
        await self.service.get_user_by_id(42, backend)
        backend.get_user_by_id.assert_awaited_with(42)
