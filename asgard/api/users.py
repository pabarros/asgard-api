from aiohttp import web
from aiohttp.web import json_response
from asyncworker import RouteTypes

from asgard.api.resources.users import (
    UserMeResource,
    UserListResource,
    UserResource,
)
from asgard.app import app
from asgard.backends.users import UsersBackend
from asgard.http.auth import auth_required
from asgard.models.account import Account
from asgard.models.user import User
from asgard.services.users import UsersService


@app.route(["/users/me"], type=RouteTypes.HTTP, methods=["GET"])
@auth_required
async def whoami(request: web.Request):
    user = await User.from_alchemy_obj(request["user"])
    current_account = await Account.from_alchemy_obj(
        request["user"].current_account
    )

    alternate_accounts = await UsersService.get_alternate_accounts(
        user, current_account, UsersBackend()
    )

    resource_response = UserMeResource(
        user=user, current_account=current_account, accounts=alternate_accounts
    )

    return json_response(resource_response.dict())


@app.route(["/users"], type=RouteTypes.HTTP, methods=["GET"])
async def users_list(request: web.Request):
    users = await UsersService.get_users(UsersBackend())
    return web.json_response(UserListResource(users=users).dict())


@app.route(["/users/{user_id}"], type=RouteTypes.HTTP, methods=["GET"])
async def user_by_id(request: web.Request):

    user_id: str = request.match_info["user_id"]
    user = await UsersService.get_user_by_id(int(user_id), UsersBackend())
    status_code = 200 if user else 404
    return web.json_response(UserResource(user=user).dict(), status=status_code)
