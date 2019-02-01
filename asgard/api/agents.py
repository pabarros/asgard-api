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


def apply_attr_filter(attr_name, attr_value, agent_attrs):
    return attr_name in agent_attrs and agent_attrs[attr_name] == attr_value


@app.route(["/agents/with-attrs"], type=RouteTypes.HTTP, methods=["GET"])
@auth_required
async def agents_with_attrs(request: web.Request):
    namespace = request["user"].current_account.namespace
    filters = request.query
    agents_info = await agents_service.get_agents(
        namespace=namespace, backend=mesos
    )
    filtered_agents = []
    for agent in agents_info["agents"]:
        all_filters = [
            apply_attr_filter(
                attr_name, filters[attr_name], agent["attributes"]
            )
            for attr_name in filters
        ]
        if all(all_filters):
            filtered_agents.append(agent)

    return web.json_response({"agents": filtered_agents})
