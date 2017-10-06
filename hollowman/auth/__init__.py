
from alchemytools.context import managed
from sqlalchemy.orm.exc import NoResultFound

from hollowman.models import HollowmanSession, User

def _get_user_by_email(email):
    with managed(HollowmanSession) as s:
        try:
            user = s.query(User).filter(User.tx_email == email).one()
            [s.expunge(acc) for acc in user.accounts]
            s.expunge(user)
            return user
        except NoResultFound:
            return None
