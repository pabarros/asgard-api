from aiohttp import web
from asyncworker import RouteTypes

from asgard.app import app
from asgard.models.job import ScheduledJob


@app.route(["/jobs"], type=RouteTypes.HTTP, methods=["POST"])
async def index_jobs(request: web.Request):
    data = await request.json()
    job = ScheduledJob(**data)
    return web.json_response(job.dict())
