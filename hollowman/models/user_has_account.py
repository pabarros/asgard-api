# necoding: utf-8

from sqlalchemy import Column, ForeignKey, Integer, Table
from sqlalchemy.orm import relation

from hollowman.models import BaseModel

# class UserHasAccount(BaseModel):
#    __tablename__ = "user_has_account"
#
#    user_id = Column(Integer, ForeignKey('user.id'))
#    user = relation("User")
#
#    account_id = Column(Integer, ForeignKey('account.id'))
#    account = relation("Account")

UserHasAccount = Table(
    "user_has_account",
    BaseModel.metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("user.id")),
    Column("account_id", Integer, ForeignKey("account.id")),
)
