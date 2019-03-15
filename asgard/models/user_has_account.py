# necoding: utf-8

from sqlalchemy import Column, ForeignKey, Integer, Table

from hollowman.models.base import BaseModel

UserHasAccount = Table(
    "user_has_account",
    BaseModel.metadata,  # type: ignore
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("user.id")),
    Column("account_id", Integer, ForeignKey("account.id")),
)
