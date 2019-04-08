from typing import Any, Dict, List, Optional

from asgard.backends.base import Orchestrator, AgentsBackend, AppsBackend
from asgard.backends.mesos.models.agent import MesosAgent
from asgard.backends.mesos.models.app import MesosApp
from asgard.backends.mesos.models.task import MesosTask
from asgard.http.client import http_client
from asgard.models.account import Account
from asgard.models.agent import Agent
from asgard.models.app import App, AppStats
from asgard.models.user import User
from asgard.sdk import mesos


async def populate_apps(agent):
    try:
        agent.applications = await agent.apps()
        agent.total_apps = len(agent.applications)
    except Exception as e:
        agent.add_error(field_name="total_apps", error_msg="INDISPONIVEL")


class MesosAgentsBackend(AgentsBackend):
    async def get_agents(
        self, user: User, account: Account
    ) -> List[MesosAgent]:
        owner = account.owner
        mesos_leader_address = await mesos.leader_address()
        agents_url = f"{mesos_leader_address}/slaves"
        async with http_client.get(agents_url) as response:
            filtered_agents = []
            data = await response.json()
            for agent_dict in data["slaves"]:
                mesos_agent = MesosAgent(**agent_dict)
                if not mesos_agent.attr_has_value("owner", owner):
                    continue
                await populate_apps(mesos_agent)
                await mesos_agent.calculate_stats()
                filtered_agents.append(mesos_agent)
        return filtered_agents

    async def get_by_id(
        self, agent_id: str, user: User, account: Account
    ) -> Optional[Agent]:
        owner = account.owner

        mesos_leader_address = await mesos.leader_address()
        agent_url = f"{mesos_leader_address}/slaves?slave_id={agent_id}"
        async with http_client.get(agent_url) as response:
            data = await response.json()
            if data["slaves"]:
                agent = MesosAgent(**data["slaves"][0])
                if not agent.attr_has_value("owner", owner):
                    return None

                await populate_apps(agent)
                await agent.calculate_stats()
                return agent
            return None

    async def get_apps_running(self, user: User, agent: Agent) -> List[App]:
        return agent.applications


class MesosOrchestrator(Orchestrator):
    async def get_agents(
        self, user: User, account: Account
    ) -> List[MesosAgent]:
        return await self.agents_backend.get_agents(user, account)

    async def get_agent_by_id(
        self, agent_id: str, user: User, account: Account
    ) -> Optional[MesosAgent]:
        return await self.agents_backend.get_by_id(agent_id, user, account)

    async def get_apps_running_for_agent(
        self, user: User, agent: Agent
    ) -> List[MesosApp]:
        return await self.agents_backend.get_apps_running(user, agent)

    async def get_app_stats(
        self, app: App, user: User, account: Account
    ) -> AppStats:
        return await self.apps_backend.get_app_stats(app, user, account)
