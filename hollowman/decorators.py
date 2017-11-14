from functools import wraps
from collections import defaultdict

import jwt
import json
from flask import request, make_response
from alchemytools.context import managed

from hollowman.conf import SECRET_KEY
from hollowman.models import HollowmanSession, User
from hollowman.log import logger
from hollowman.auth import _get_user_by_email, _get_user_by_authkey, _get_account_by_id


invalid_token_response_body = json.dumps({"msg": "Authorization token is invalid"})
permission_denied_on_account_response_body = json.dumps({"msg": "Permission Denied to access this account"})
no_associated_account_response_error = json.dumps({"msg": "No associated account"})
account_does_not_exist_response_error = json.dumps({"msg": "Account does not exist"})

class TokenTypes(object):
    USER_TOKEN = "Token"
    JWT = "JWT"

def check_auth_token(token):
    with managed(HollowmanSession) as s:
        user = _get_user_by_authkey(token)
        if not user:
            logger.info({"auth": "failed", "token-type": "apikey", "error": "Key not found", "token": token})
            return None
        return user

def check_jwt_token(jwt_token):
    try:
        payload = jwt.decode(jwt_token, key=SECRET_KEY)
        return _get_user_by_email(payload["user"]["email"])
    except Exception as e:
        logger.info({"auth": "failed", "token-type": "jwt", "error": str(e), "jwt_token": jwt_token})
        return None

def _extract_account_id_from_jwt(jwt_token):
    try:
        return jwt.decode(jwt_token, key=SECRET_KEY)["current_account"]["id"]
    except Exception:
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
                auth_header = request.headers.get("Authorization", "invalid-type invalid-token")
                token_type, token = auth_header.strip().split(" ")
                user = AUTH_TYPES[token_type](token)

                if not user:
                    return make_response(invalid_token_response_body, 401)

                if not user.accounts:
                    return make_response(no_associated_account_response_error, 401)

                request_account_id = request.args.get("account_id") or _extract_account_id_from_jwt(token)
                request_account_on_db = _get_account_by_id(request_account_id or user.accounts[0].id)
                if request_account_id and not request_account_on_db:
                    return make_response(account_does_not_exist_response_error, 401)

                user_account_ids = [acc.id for acc in user.accounts]
                if request_account_on_db.id and request_account_on_db.id not in user_account_ids:
                    return make_response(permission_denied_on_account_response_body, 401)


                request.user = user
                request.user.current_account = request_account_on_db

            except Exception as e:
                logger.exception({"exc": e, "step": "auth"})
                return make_response(invalid_token_response_body, 401)

            return fn(*args, **kwargs)
        return decorator
    return wrapper
