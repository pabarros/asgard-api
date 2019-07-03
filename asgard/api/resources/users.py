from typing import List

from pydantic import BaseModel

from asgard.models.account import Account
from asgard.models.user import User


class UserMeResource(BaseModel):
    user: User
    current_account: Account
    accounts: List[Account] = []


class UserListResource(BaseModel):
    users: List[User] = []
