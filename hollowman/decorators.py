#encoding: utf-8

from functools import wraps
from collections import defaultdict

import jwt
import json
from flask import request, make_response
from alchemytools.context import managed

from hollowman.auth.jwt import jwt_auth
from hollowman.conf import SECRET_KEY, HOLLOWMAN_ENFORCE_AUTH
from hollowman.models import HollowmanSession, User
from hollowman.log import logger


invalid_token_response_body = json.dumps({"msg": "Authorization token is invalid"})


class TokenTypes(object):
    USER_TOKEN = "Token"
    JWT = "JWT"

def check_auth_token(token):
    with managed(HollowmanSession) as s:
        _query = s.query(User).filter_by(tx_authkey=token)
        user = _query.count()
        if not user:
            logger.info({"auth": "failed", "token-type": "apikey", "error": "Key not found"})
            return None
        return _query.all()[0].tx_email

def check_jwt_token(token):
    try:
        jwt_token = jwt_auth.request_callback()
        payload = jwt.decode(jwt_token, key=SECRET_KEY)
        return payload["email"]
    except Exception as e:
        logger.info({"auth": "failed", "token-type": "jwt", "error": str(e)})
        return None

def not_authenticated(_):
    return None

AUTH_TYPES = defaultdict(lambda: not_authenticated)
AUTH_TYPES[TokenTypes.USER_TOKEN] = check_auth_token
AUTH_TYPES[TokenTypes.JWT] = check_jwt_token

def auth_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            try:
                auth_header = request.headers.get("Authorization", " ")
                token_type, token = auth_header.split(" ")
                authenticated_user = AUTH_TYPES[token_type](token)

                if HOLLOWMAN_ENFORCE_AUTH and not authenticated_user:
                    return make_response(invalid_token_response_body, 401)

                request.user = authenticated_user
                return fn(*args, **kwargs)
            except Exception as e:
                logger.error({"exc": e, "step": "auth"})
                return make_response(invalid_token_response_body, 401)
        return decorator
    return wrapper
