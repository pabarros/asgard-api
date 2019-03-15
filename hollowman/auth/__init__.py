from alchemytools.context import managed
from sqlalchemy.orm.exc import NoResultFound

from hollowman.models import Account, HollowmanSession, User


def _expunge_user_and_accounts(session, user):
    for acc in user.accounts:
        session.expunge(acc)

    session.expunge(user)


def _get_user_by_email(email):
    with managed(HollowmanSession) as s:
        try:
            user = s.query(User).filter(User.tx_email == email).one()
            _expunge_user_and_accounts(s, user)
            return user
        except NoResultFound:
            return None


def _get_user_by_authkey(key):
    with managed(HollowmanSession) as s:
        try:
            user = s.query(User).filter(User.tx_authkey == key).one()
            _expunge_user_and_accounts(s, user)
            return user
        except NoResultFound:
            return None


def _get_account_by_id(account_id):
    acc = None
    with managed(HollowmanSession) as s:
        if account_id:
            acc = s.query(Account).get(account_id)
            if acc:
                s.expunge(acc)
        return acc
