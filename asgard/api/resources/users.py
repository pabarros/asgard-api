from typing import List, Optional

from pydantic import BaseModel

from asgard.models.account import Account
from asgard.models.user import User


class UserMeResource(BaseModel):
    user: User
    current_account: Account
    accounts: List[Account] = []


class UserListResource(BaseModel):
    users: List[User] = []


class UserResource(BaseModel):
    user: Optional[User]


class ErrorDetail(BaseModel):
    msg: str


class ErrorResource(BaseModel):
    errors: List[ErrorDetail]


class UserAccountsResource(BaseModel):
    accounts: List[Account] = []
