from asynctest import TestCase, CoroutineMock

from asgard.services.accounts import AccountsService


class AccountServiceTest(TestCase):
    async def test_calls_backend_with_correct_parameters(self):
        backend = CoroutineMock(get_account_by_id=CoroutineMock())
        account_id = 42
        await AccountsService.get_account_by_id(account_id, backend)
        backend.get_account_by_id.assert_awaited_with(account_id)
