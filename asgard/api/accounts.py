from aiohttp import web
from asyncworker import RouteTypes

from asgard.app import app
from asgard.backends.accounts import AccountsBackend
from asgard.http.auth import auth_required
from asgard.http.auth.jwt import jwt_encode
from asgard.models.user import User
from asgard.services.accounts import AccountsService


@app.route(
    ["/accounts/{account_id}/auth"], type=RouteTypes.HTTP, methods=["GET"]
)
@auth_required
async def change_account(request: web.Request):
    account_id: str = request.match_info["account_id"]
    user = await User.from_alchemy_obj(request["user"])
    permission_ok = False
    new_token = b""

    account = await AccountsService.get_account_by_id(
        int(account_id), AccountsBackend()
    )
    if account:
        permission_ok = await account.user_has_permission(user)

    if permission_ok:
        new_token = jwt_encode(user, account)
        return web.json_response(headers={"JWT": new_token.decode("utf-8")})

    return web.json_response(status=403)
