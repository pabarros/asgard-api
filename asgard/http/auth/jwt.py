from datetime import datetime, timedelta

import jwt

from asgard.models.account import Account
from asgard.models.user import User
from hollowman.conf import SECRET_KEY


def jwt_encode(user: User, account: Account) -> bytes:
    """
    Encodes a new JWT Token
    https://tools.ietf.org/html/rfc7519#section-4.1.5
    """
    issued_at = datetime.utcnow()
    expiration_time = issued_at + timedelta(days=7)
    not_before = issued_at + timedelta(seconds=0)
    return jwt.encode(
        {
            "exp": expiration_time,
            "iat": issued_at,
            "nbf": not_before,
            "user": user.dict(),
            "current_account": account.dict(),
        },
        SECRET_KEY,
    )
