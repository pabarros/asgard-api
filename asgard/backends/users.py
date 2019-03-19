from typing import List

from asgard.db import AsgardDBSession
from asgard.models.account import Account, AccountDB
from asgard.models.user import User, UserDB
from asgard.models.user_has_account import UserHasAccount


class UsersBackend:
    async def get_alternate_accounts(
        self, user: User, current_account: Account
    ) -> List[Account]:

        _join = UserDB.__table__.join(
            UserHasAccount, UserDB.id == UserHasAccount.c.user_id, isouter=True
        ).join(
            AccountDB.__table__,
            AccountDB.id == UserHasAccount.c.account_id,
            isouter=True,
        )
        async with AsgardDBSession() as s:
            accounts = (
                await s.query(AccountDB)
                .join(_join)
                .filter(UserDB.tx_email == user.email)
                .filter(AccountDB.id != current_account.id)
                .all()
            )
            all_acc = [await Account.from_alchemy_obj(acc) for acc in accounts]
        return all_acc
