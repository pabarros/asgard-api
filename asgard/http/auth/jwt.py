from datetime import datetime, timedelta

import jwt

from hollowman.conf import SECRET_KEY


def jwt_encode(user_info):
    iat = datetime.utcnow()
    exp = iat + timedelta(days=7)
    nbf = iat + timedelta(seconds=0)
    return jwt.encode(
        {
            "exp": exp,
            "iat": iat,
            "nbf": nbf,
            "user": user_info.get("user"),
            "current_account": user_info.get("current_account"),
        },
        SECRET_KEY,
    )
