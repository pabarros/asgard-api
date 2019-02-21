from typing import List, Type, Dict, Any
from decimal import Decimal
from asgard.app import app
from asyncworker import RouteTypes
from asyncworker.conf import settings
from aiohttp import web
import aiohttp_cors


from asgard.math import round_up
from asgard.services import agents_service
from asgard.backends import mesos
from asgard.http.auth import auth_required

from asgard.services.models import Model
from asgard.services.models.agent import Agent

from asgard.api.resources.agents import AgentsResource
from asgard.api.resources.apps import AppsResource


def calculate_stats(agents):
    total_cpus = sum(
        [Decimal(agent.resources["cpus"]) for agent in agents]
    ) or Decimal("1")
    total_used_cpus = sum(
        [Decimal(agent.used_resources["cpus"]) for agent in agents]
    )

    total_ram = sum(
        [Decimal(agent.resources["mem"]) for agent in agents]
    ) or Decimal("1")
    total_used_ram = sum(
        [Decimal(agent.used_resources["mem"]) for agent in agents]
    )

    return {
        "cpu_pct": str(round_up(total_used_cpus / total_cpus * 100)),
        "ram_pct": str(round_up(total_used_ram / total_ram * 100)),
    }


@app.route(["/agents"], type=RouteTypes.HTTP, methods=["GET"])
@auth_required
async def agents_handler(request: web.Request):
    namespace = request["user"].current_account.namespace
    agents = await agents_service.get_agents(namespace=namespace, backend=mesos)
    stats = calculate_stats(agents)
    return web.json_response(AgentsResource(agents=agents, stats=stats).dict())


def apply_attr_filter(
    filters_dict: Dict[str, Any], agents: List[Agent]
) -> List[Agent]:

    filtered_agents = []
    for agent in agents:
        all_filters = [
            agent.attr_has_value(attr_name, filters_dict[attr_name])
            for attr_name in filters_dict
        ]
        if all(all_filters):
            filtered_agents.append(agent)
    return filtered_agents


@app.route(["/agents/with-attrs"], type=RouteTypes.HTTP, methods=["GET"])
@auth_required
async def agents_with_attrs(request: web.Request):
    namespace = request["user"].current_account.namespace
    filters = request.query.copy()
    filters.pop("account_id", None)

    agents = await agents_service.get_agents(namespace=namespace, backend=mesos)
    filtered_agents = apply_attr_filter(filters, agents)

    stats = calculate_stats(filtered_agents)
    return web.json_response(
        AgentsResource(agents=filtered_agents, stats=stats).dict()
    )


@app.route(["/agents/{agent_id}/apps"], type=RouteTypes.HTTP, methods=["GET"])
@auth_required
async def agent_apps(request: web.Request):
    namespace = request["user"].current_account.namespace
    agent_id = request.match_info["agent_id"]
    apps = await agents_service.get_apps(
        namespace=namespace, agent_id=agent_id, backend=mesos
    )
    return web.json_response(AppsResource(apps=apps).dict())


async def patched_startup(app):

    app[RouteTypes.HTTP] = {}
    routes = app.routes_registry.http_routes
    if not routes:
        return

    app[RouteTypes.HTTP]["app"] = http_app = web.Application()
    for route in routes:
        http_app.router.add_route(**route)

    cors = aiohttp_cors.setup(
        http_app,
        defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True, expose_headers="*", allow_headers="*"
            )
        },
    )

    # Configure CORS on all routes.
    for route in list(http_app.router.routes()):
        cors.add(route)

    app[RouteTypes.HTTP]["runner"] = web.AppRunner(http_app)
    await app[RouteTypes.HTTP]["runner"].setup()
    app[RouteTypes.HTTP]["site"] = web.TCPSite(
        runner=app[RouteTypes.HTTP]["runner"],
        host=settings.HTTP_HOST,
        port=settings.HTTP_PORT,
    )

    await app[RouteTypes.HTTP]["site"].start()


app._on_startup.clear()
app._on_startup.append(patched_startup)
