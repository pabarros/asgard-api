# encoding: utf-8

from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from asgard.models.user_has_account import UserHasAccount
from hollowman.models.base import BaseModel


class User(BaseModel):  # type: ignore
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    accounts = relationship("Account", secondary=UserHasAccount)
    tx_name = Column(String, nullable=False)
    tx_email = Column(String, nullable=False, unique=True)
    tx_authkey = Column(String(32), nullable=True, unique=True)
    bl_system = Column(Boolean, nullable=False, default=False)
