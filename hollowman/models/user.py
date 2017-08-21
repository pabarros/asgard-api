#encoding: utf-8

from sqlalchemy import Column, Integer, String, Sequence, Boolean
from sqlalchemy.orm import relationship

from hollowman.models import BaseModel
from hollowman.models.user_has_account import UserHasAccount

class User(BaseModel):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    tx_name = Column(String, nullable=False)
    tx_email = Column(String, nullable=False, unique=True)
    tx_authkey = Column(String(32), nullable=True, unique=True)
    bl_system = Column(Boolean, nullable=False, default=False)

