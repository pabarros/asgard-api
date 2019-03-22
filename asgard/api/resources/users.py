from typing import List

from pydantic import BaseModel

from asgard.models.account import Account
from asgard.models.user import User


class UserResource(BaseModel):
    user: User
    current_account: Account
    accounts: List[Account] = []
