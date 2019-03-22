from typing import List

from asgard.db import AsgardDBSession
from asgard.models.account import Account
from asgard.models.user import User
from asgard.models.user_has_account import UserHasAccount


class UsersBackend:
    async def get_alternate_accounts(
        self, user: User, current_account: Account
    ) -> List[Account]:
        _, UserTable = await user.to_alchemy_obj()
        _, AccountTable = await current_account.to_alchemy_obj()

        _join = UserTable.__table__.join(
            UserHasAccount,
            UserTable.id == UserHasAccount.c.user_id,
            isouter=True,
        ).join(
            AccountTable.__table__,
            AccountTable.id == UserHasAccount.c.account_id,
            isouter=True,
        )
        async with AsgardDBSession() as s:
            accounts = (
                await s.query(AccountTable)
                .join(_join)
                .filter(UserTable.tx_email == user.email)
                .filter(AccountTable.id != current_account.id)
                .all()
            )
            all_acc = [await Account.from_alchemy_obj(acc) for acc in accounts]
        return all_acc
