#encoding: utf-8

from functools import wraps

import jwt
from flask import request

from hollowman.auth.jwt import jwt_auth
from hollowman.conf import SECRET_KEY

def populate_user():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            jwt_token = jwt_auth.request_callback()
            request.user = None
            try:
                payload = jwt.decode(jwt_token, key=SECRET_KEY)
                request.user = payload["email"]
            except:
                pass
            return fn(*args, **kwargs)
        return decorator
    return wrapper
