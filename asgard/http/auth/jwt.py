from datetime import datetime, timedelta

import jwt

from asgard.models.account import Account
from asgard.models.user import User
from hollowman.conf import SECRET_KEY


def jwt_encode(user: User, account: Account) -> bytes:
    iat = datetime.utcnow()
    exp = iat + timedelta(days=7)
    nbf = iat + timedelta(seconds=0)
    return jwt.encode(
        {
            "exp": exp,
            "iat": iat,
            "nbf": nbf,
            "user": user.dict(),
            "current_account": account.dict(),
        },
        SECRET_KEY,
    )
