from asgard.app import app
from asyncworker import RouteTypes
from aiohttp import web

from asgard.services import agents_service
from asgard.backends import mesos


@app.route(["/agents"], type=RouteTypes.HTTP, methods=["GET"])
async def agents_handler(request: web.Request):
    agents_info = await agents_service.get_agents(namespace="", backend=mesos)
    return web.json_response(agents_info)
