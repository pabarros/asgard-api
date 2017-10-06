#encoding: utf-8

from sqlalchemy import Column, Integer, String, Sequence
from sqlalchemy.orm import relationship

from hollowman.models import BaseModel
from hollowman.models.user_has_account import UserHasAccount
from hollowman.models.user import User

class Account(BaseModel):
    __tablename__ = "account"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    users = relationship(User, secondary=UserHasAccount, backref="accounts")
    namespace = Column(String, nullable=False)
    owner = Column(String, nullable=False)

