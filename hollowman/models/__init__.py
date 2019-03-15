# encoding: utf-8

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from asgard.models.account import Account
from asgard.models.user import User
from asgard.models.user_has_account import UserHasAccount
from hollowman.conf import HOLLOWMAN_DB_ECHO, HOLLOWMAN_DB_URL

engine = create_engine(HOLLOWMAN_DB_URL, echo=HOLLOWMAN_DB_ECHO)
HollowmanSession = sessionmaker(bind=engine)
