# necoding: utf-8

from sqlalchemy import Column, ForeignKey, Integer, Table

from asgard.models.base import BaseModelAlchemy

UserHasAccount = Table(
    "user_has_account",
    BaseModelAlchemy.metadata,  # type: ignore
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("user.id")),
    Column("account_id", Integer, ForeignKey("account.id")),
)
