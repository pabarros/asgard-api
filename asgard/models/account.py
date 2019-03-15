# encoding: utf-8

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from asgard.models.user_has_account import UserHasAccount
from hollowman.models.base import BaseModel


class Account(BaseModel):  # type: ignore
    __tablename__ = "account"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    users = relationship("User", secondary=UserHasAccount)
    namespace = Column(String, nullable=False)
    owner = Column(String, nullable=False)
