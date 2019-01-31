from asgard.backends.base import Backend

from asgard.sdk import mesos
from asgard.http.client import http_client


class MesosAgent:
    def __init__(self, data):
        self._data = data

    def has_attribute(self, attr_name):
        return attr_name in self._data["attributes"]

    def _get_attribute_value(self, attr_name):
        return self._data["attributes"][attr_name]

    def attr_has_value(self, attr_name, attr_value):
        return (
            self.has_attribute(attr_name)
            and self._get_attribute_value(attr_name) == attr_value
        )


class MesosBackend(Backend):
    async def get_agents(self, namespace: str):
        mesos_leader_address = await mesos.leader_address()
        agents_url = f"{mesos_leader_address}/slaves"
        async with http_client.get(agents_url) as response:
            filtered_agents = []
            data = await response.json()
            for agent in data["slaves"]:
                mesos_agent = MesosAgent(agent)
                if not mesos_agent.attr_has_value("owner", namespace):
                    continue
                agent.pop("pid", None)
                agent.pop("registered_time", None)
                agent.pop("offered_resources", None)
                agent.pop("reserved_resources", None)
                agent.pop("unreserved_resources", None)
                agent.pop("capabilities", None)
                agent.pop("reserved_resources_full", None)
                agent.pop("unreserved_resources_full", None)
                agent.pop("used_resources_full", None)
                agent.pop("offered_resources_full", None)
                filtered_agents.append(agent)
        return {"agents": filtered_agents}
