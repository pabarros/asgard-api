from typing import Optional, List

from sqlalchemy.orm.exc import NoResultFound

from asgard.db import AsgardDBSession
from asgard.models.account import Account, AccountDB
from asgard.models.user import User, UserDB
from asgard.models.user_has_account import UserHasAccount


class AccountsBackend:
    async def get_account_by_id(self, acc_id: int) -> Optional[Account]:
        try:
            async with AsgardDBSession() as s:
                result = (
                    await s.query(AccountDB)
                    .filter(AccountDB.id == acc_id)
                    .one()
                )
                return await Account.from_alchemy_obj(result)
        except NoResultFound:
            return None

    async def get_accounts(self) -> List[Account]:
        async with AsgardDBSession() as s:
            result = await s.query(AccountDB).all()
            accounts = [await Account.from_alchemy_obj(item) for item in result]
            return accounts

    async def get_users_from_account(self, account: Account) -> List[User]:
        async with AsgardDBSession() as s:
            _join = UserHasAccount.join(
                UserDB, UserHasAccount.c.user_id == UserDB.id
            )
            users = (
                await s.query(UserDB)
                .join(
                    UserHasAccount.join(
                        UserDB, UserHasAccount.c.user_id == UserDB.id
                    )
                )
                .filter(UserHasAccount.c.account_id == account.id)
                .all()
            )
            return [await User.from_alchemy_obj(u) for u in users]
