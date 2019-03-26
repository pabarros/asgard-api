from aiohttp import web
from asyncworker import RouteTypes

from asgard.api.resources.apps import AppStatsResource
from asgard.app import app
from asgard.backends.apps import AppsBackend
from asgard.models.account import Account
from asgard.models.user import User
from asgard.services.apps import AppsService


@app.route(["apps/{app_id}/stats"], type=RouteTypes.HTTP, methods=["GET"])
async def app_stats(request: web.Request):
    app_id: str = request.match_info["app_id"]
    timeframe: str = request.match_info["timeframe"]
    user = await User.from_alchemy_obj(request["user"])

    account = await Account.from_alchemy_obj(user.current_account)
    stats = await AppsService.get_app_stats(
        app_id, timeframe, user, account, AppsBackend()
    )

    return web.json_response(AppStatsResource(stats=stats))
