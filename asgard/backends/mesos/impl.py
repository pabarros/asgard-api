from typing import Any, Dict, List, Optional

from asgard.backends.base import Backend
from asgard.backends.mesos.models import MesosAgent, MesosApp, MesosTask
from asgard.http.client import http_client
from asgard.sdk import mesos


class MesosBackend(Backend):
    async def populate_apps(self, agent):
        try:
            agent.applications = await agent.apps()
            agent.total_apps = len(agent.applications)
        except Exception as e:
            agent.add_error(field_name="total_apps", error_msg="INDISPONIVEL")

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
                await self.populate_apps(mesos_agent)
                await mesos_agent.calculate_stats()
                filtered_agents.append(mesos_agent)
        return filtered_agents

    async def get_agent_by_id(
        self, namespace: str, agent_id: str
    ) -> Optional[MesosAgent]:
        mesos_leader_address = await mesos.leader_address()
        agent_url = f"{mesos_leader_address}/slaves?slave_id={agent_id}"
        async with http_client.get(agent_url) as response:
            data = await response.json()
            if data["slaves"]:
                agent = MesosAgent(**data["slaves"][0])
                if not agent.attr_has_value("owner", namespace):
                    return None

                await self.populate_apps(agent)
                await agent.calculate_stats()
                return agent
            return None

    async def get_apps(self, namespace: str, agent_id: str) -> List[MesosApp]:
        agent = await self.get_agent_by_id(namespace, agent_id)
        if agent:
            return agent.applications
        return []

    async def get_tasks(
        self, namespace: str, agent_id: str, app_id: str
    ) -> List[MesosTask]:
        pass
