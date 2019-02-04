from typing import Dict, Union, List, Any
from asgard.backends.base import Backend

from asgard.sdk import mesos
from asgard.http.client import http_client


from asgard.services.models.agent import Agent


class MesosAgent(Agent):
    _type: str = "MESOS"
    type: str = "MESOS"
    id: str
    hostname: str
    active: bool
    version: str
    port: int
    used_resources: Dict[str, Union[str, int]]
    attributes: Dict[str, str]
    resources: Dict[str, Union[str, int]]


class MesosBackend(Backend):
    async def get_agents(
        self, namespace: str, attr_filters: Dict[str, Any] = {}
    ) -> List[MesosAgent]:
        mesos_leader_address = await mesos.leader_address()
        agents_url = f"{mesos_leader_address}/slaves"
        async with http_client.get(agents_url) as response:
            filtered_agents = []
            data = await response.json()
            for agent_dict in data["slaves"]:
                mesos_agent = MesosAgent(**agent_dict)
                if not mesos_agent.attr_has_value("owner", namespace):
                    continue
                filtered_agents.append(mesos_agent)
        return filtered_agents
