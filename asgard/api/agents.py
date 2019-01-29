from asgard.app import app
from asyncworker import RouteTypes
from aiohttp import web

from asgard.services import agents_service
from asgard.backends import mesos
from asgard.http.auth import auth_required


@app.route(["/agents"], type=RouteTypes.HTTP, methods=["GET"])
@auth_required
async def agents_handler(request: web.Request):
    namespace = request["user"].current_account.namespace
    agents_info = await agents_service.get_agents(
        namespace=namespace, backend=mesos
    )
    return web.json_response(agents_info)
