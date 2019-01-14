from asgard.app import app
from asyncworker import RouteTypes
from aiohttp import web


@app.route(["/agents"], type=RouteTypes.HTTP, methods=["GET"])
async def agents_handler(request):
    return web.json_response({"agents": "OK"})
