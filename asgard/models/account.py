# encoding: utf-8

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from asgard.models.base import BaseModel, ModelFactory, BaseModelAlchemy
from asgard.models.user_has_account import UserHasAccount


class AccountDB(BaseModelAlchemy):  # type: ignore
    __tablename__ = "account"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    users = relationship("UserDB", secondary=UserHasAccount)
    namespace = Column(String, nullable=False)
    owner = Column(String, nullable=False)


class Account(BaseModel):
    type: str = "ASGARD"
    id: int
    name: str
    namespace: str
    owner: str

    @staticmethod
    async def from_alchemy_obj(alchemy_obj: AccountDB) -> "Account":
        return Account(
            id=alchemy_obj.id,
            name=alchemy_obj.name,
            namespace=alchemy_obj.namespace,
            owner=alchemy_obj.owner,
        )


AccountFactory = ModelFactory(Account)
