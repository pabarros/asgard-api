from typing import List

from asgard.backends.users import UsersBackend
from asgard.models.account import Account
from asgard.models.user import User


class UsersService:
    @staticmethod
    async def get_alternate_accounts(
        user: User, current_account: Account, backend: UsersBackend
    ) -> List[Account]:
        return await backend.get_alternate_accounts(user, current_account)
