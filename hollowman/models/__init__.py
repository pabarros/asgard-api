# encoding: utf-8

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from hollowman.conf import HOLLOWMAN_DB_ECHO, HOLLOWMAN_DB_URL

from .account import Account
from .user import User
from .user_has_account import UserHasAccount

engine = create_engine(HOLLOWMAN_DB_URL, echo=HOLLOWMAN_DB_ECHO)
HollowmanSession = sessionmaker(bind=engine)

BaseModel = declarative_base()
