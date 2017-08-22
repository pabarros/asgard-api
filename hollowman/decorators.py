#encoding: utf-8

from functools import wraps

import jwt
import json
from flask import request, make_response
from alchemytools.context import managed

from hollowman.auth.jwt import jwt_auth
from hollowman.conf import SECRET_KEY, HOLLOWMAN_ENFORCE_AUTH
from hollowman.models import HollowmanSession, User
from hollowman.log import logger


invalid_token_response_body = json.dumps({"msg": "Authorization token is invalid"})

def check_auth_token():
    auth_header = request.headers.get("Authorization", " ")
    token = auth_header.split(" ")[1]
    with managed(HollowmanSession) as s:
        _query = s.query(User).filter_by(tx_authkey=token)
        user = _query.count()
        if not user:
            return None
        return _query.all()[0].tx_email

def check_jwt_token():
    try:
        jwt_token = jwt_auth.request_callback()
        payload = jwt.decode(jwt_token, key=SECRET_KEY)
        return payload["email"]
    except Exception as e:
        return None

def auth_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            try:
                email_by_token = check_auth_token()
                email_by_jwt = check_jwt_token()

                authenticated = any([email_by_jwt, email_by_token])
                if HOLLOWMAN_ENFORCE_AUTH and not authenticated:
                    return make_response(invalid_token_response_body, 401)

                request.user = email_by_token
                if email_by_jwt:
                    request.user = email_by_jwt
                return fn(*args, **kwargs)
            except Exception as e:
                logger.error({"exc": e, "step": "auth"})
                return make_response(invalid_token_response_body, 401)
        return decorator
    return wrapper
