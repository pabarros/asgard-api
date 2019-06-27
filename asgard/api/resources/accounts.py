from typing import List, Optional

from pydantic import BaseModel

from asgard.models.account import Account


class AccountsResource(BaseModel):
    accounts: List[Account] = []


class AccountResource(BaseModel):
    account: Optional[Account]
