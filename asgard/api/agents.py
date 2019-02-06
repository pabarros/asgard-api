from typing import List, Type, Dict, Any
from asgard.app import app
from asyncworker import RouteTypes
from aiohttp import web


from asgard.services import agents_service
from asgard.backends import mesos
from asgard.http.auth import auth_required

from asgard.services.models import Model
from asgard.services.models.agent import Agent

from asgard.api.resources.agents import AgentsResource
from asgard.api.resources.apps import AppsResource


@app.route(["/agents"], type=RouteTypes.HTTP, methods=["GET"])
@auth_required
async def agents_handler(request: web.Request):
    namespace = request["user"].current_account.namespace
    agents = await agents_service.get_agents(namespace=namespace, backend=mesos)
    return web.json_response(AgentsResource(agents=agents).dict())


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
    filters = request.query
    agents = await agents_service.get_agents(namespace=namespace, backend=mesos)
    filtered_agents = apply_attr_filter(filters, agents)

    return web.json_response(AgentsResource(agents=filtered_agents).dict())


@app.route(["/agents/{agent_id}/apps"], type=RouteTypes.HTTP, methods=["GET"])
@auth_required
async def agent_apps(request: web.Request):
    namespace = request["user"].current_account.namespace
    agent_id = request.match_info["agent_id"]
    apps = await agents_service.get_apps(
        namespace=namespace, agent_id=agent_id, backend=mesos
    )
    return web.json_response(AppsResource(apps=apps).dict())
