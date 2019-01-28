from functools import wraps
from collections import defaultdict
from typing import Dict, Callable

from aiohttp import web
from sqlalchemy.orm.exc import NoResultFound

import jwt
import json

from asgard import db

from hollowman.conf import SECRET_KEY
from hollowman.models import HollowmanSession, User, Account, UserHasAccount
from hollowman.log import logger
from hollowman.auth import _get_user_by_email


invalid_token_response_body = {"msg": "Authorization token is invalid"}
permission_denied_on_account_response_body = {
    "msg": "Permission Denied to access this account"
}
no_associated_account_response_error = {"msg": "No associated account"}
account_does_not_exist_response_error = {"msg": "Account does not exist"}


def make_response(json_data, status_code):
    return web.json_response(json_data, status=status_code)


class TokenTypes(object):
    USER_TOKEN = "Token"
    JWT = "JWT"


async def _get_account_by_id(account_id):
    async with db.AsgardDBSession() as s:
        if account_id:
            try:
                acc = await s.query(Account).filter(Account.id == account_id).one()
                return acc
            except NoResultFound:
                return None
    return None


async def check_auth_token(token):
    async with db.AsgardDBSession() as session:
        _join = User.__table__.join(
            UserHasAccount, User.id == UserHasAccount.c.user_id, isouter=True
        ).join(
            Account.__table__, Account.id == UserHasAccount.c.account_id, isouter=True
        )
        rows = (
            await session.query(User, Account.id.label("account_id"))
            .join(_join)
            .filter(User.tx_authkey == token)
            .all()
        )
        if not rows:
            logger.info(
                {
                    "event": "auth-failed",
                    "token-type": "apikey",
                    "error": "Key not found",
                    "token": token,
                }
            )
            return None
        account_ids = [row.account_id for row in rows if row.account_id]
        user = User(tx_name=rows[0].tx_name, tx_email=rows[0].tx_email)
        user.account_ids = account_ids
        return user


def check_jwt_token(jwt_token):
    try:
        payload = jwt.decode(jwt_token, key=SECRET_KEY)
        return _get_user_by_email(payload["user"]["email"])
    except Exception as e:
        logger.info(
            {
                "auth": "failed",
                "token-type": "jwt",
                "error": str(e),
                "jwt_token": jwt_token,
            }
        )
        return None


def _extract_account_id_from_jwt(jwt_token):
    try:
        return jwt.decode(jwt_token, key=SECRET_KEY)["current_account"]["id"]
    except Exception:
        return None


def not_authenticated(_):
    return None


AUTH_TYPES: Dict[str, Callable] = defaultdict(lambda: not_authenticated)
AUTH_TYPES[TokenTypes.USER_TOKEN] = check_auth_token
AUTH_TYPES[TokenTypes.JWT] = check_jwt_token


def auth_required(fn):
    @wraps(fn)
    async def wrapper(request: web.Request, *args, **kwargs):
        try:
            user = None
            auth_header = request.headers.get(
                "Authorization", "invalid-type invalid-token"
            )
            token_type, token = auth_header.strip().split(" ")

            user = await AUTH_TYPES[token_type](token)

            if not user:
                return make_response(invalid_token_response_body, 401)

            if not user.account_ids:
                return make_response(no_associated_account_response_error, 401)

            request_account_id = request.query.get(
                "account_id"
            ) or _extract_account_id_from_jwt(token)
            request_account_on_db = await _get_account_by_id(
                request_account_id or user.account_ids[0]
            )
            if request_account_id and not request_account_on_db:
                return make_response(account_does_not_exist_response_error, 401)

            if (
                request_account_on_db.id
                and request_account_on_db.id not in user.account_ids
            ):
                return make_response(permission_denied_on_account_response_body, 401)

            request.user = user
            request.user.current_account = request_account_on_db

        except Exception as e:
            logger.exception({"exc": e, "step": "auth"})
            return make_response(invalid_token_response_body, 401)

        user.current_account = request_account_on_db
        request.user = user
        return await fn(request, *args, **kwargs)

    return wrapper
