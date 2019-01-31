from aiohttp import web

from asgard.app import app
from asyncworker import RouteTypes


@app.route(["/"], methods=["GET"], type=RouteTypes.HTTP)
async def handle(r):
    return web.json_response({"OK": True})
