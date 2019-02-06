from typing import Dict, Union, List, Any, Optional
from asgard.backends.base import Backend

from asgard.sdk import mesos
from asgard.http.client import http_client


from asgard.services.models.agent import Agent
from asgard.services.models.app import App


class MesosApp(App):
    _type: str = "MESOS"
    type: str = "MESOS"
    id: str


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

    def filter_by_attrs(self, kv):
        pass

    def _transform_to_asgard_app_id(self, executor_id: str) -> str:
        task_name_part = executor_id.split(".")[0]
        return "/".join(task_name_part.split("_")[1:])

    async def apps(self) -> List[App]:
        self_address = f"http://{self.hostname}:{self.port}"
        containers_url = f"{self_address}/containers"
        apps = []
        async with http_client.get(containers_url) as response:
            data = await response.json()
            for container_info in data:
                apps.append(
                    MesosApp(
                        **{
                            "id": self._transform_to_asgard_app_id(
                                container_info["executor_id"]
                            )
                        }
                    )
                )
            return apps


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

    async def get_agent_by_id(
        self, namespace: str, agent_id: str
    ) -> Optional[Agent]:
        mesos_leader_address = await mesos.leader_address()
        agent_url = f"{mesos_leader_address}/slaves?slave_id={agent_id}"
        async with http_client.get(agent_url) as response:
            data = await response.json()
            if len(data["slaves"]):
                agent = MesosAgent(**data["slaves"][0])
                if not agent.attr_has_value("owner", namespace):
                    return None
                return agent
            return None

    async def get_apps(self, namespace: str, agent_id: str) -> List[App]:
        agent = await self.get_agent_by_id(namespace, agent_id)
        if agent:
            return await agent.apps()
        return []
