from typing import List, Type, Dict
from asgard.app import app
from asyncworker import RouteTypes
from aiohttp import web


from asgard.services import agents_service
from asgard.backends import mesos
from asgard.http.auth import auth_required

from asgard.services.models import Model
from asgard.services.models.agent import Agent

from asgard.api.resources.agents import AgentsResource


@app.route(["/agents"], type=RouteTypes.HTTP, methods=["GET"])
@auth_required
async def agents_handler(request: web.Request):
    namespace = request["user"].current_account.namespace
    agents = await agents_service.get_agents(namespace=namespace, backend=mesos)
    return web.json_response(AgentsResource(agents=agents).dict())


def check_attr_value(attr_name, attr_value, agent_attrs):
    return attr_name in agent_attrs and agent_attrs[attr_name] == attr_value


def apply_attr_filter(filters_dict: Dict, agents: List[Agent]) -> List[Agent]:

    filtered_agents = []
    for agent in agents:
        all_filters = [
            check_attr_value(
                attr_name, filters_dict[attr_name], agent.attributes
            )
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
