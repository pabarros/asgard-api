from typing import List, Optional

from asgard.backends.base import Orchestrator
from asgard.models.account import Account
from asgard.models.agent import Agent
from asgard.models.app import App
from asgard.models.user import User


class AgentsService:
    async def get_agents(
        self, user: User, account: Account, backend: Orchestrator
    ) -> List[Agent]:
        """
        Lista todos os agentes de cluster asgard. Essa litsa vem do orquestrador que é passado como parametro.
        """
        return await backend.get_agents(user, account)

    async def get_apps_running_for_agent(
        self, user: User, agent: Agent, backend: Orchestrator
    ) -> List[App]:
        return await backend.get_apps_running_for_agent(user, agent)

    async def get_agent_by_id(
        self, agent_id: str, user: User, account: Account, backend: Orchestrator
    ) -> Optional[Agent]:
        return await backend.get_agent_by_id(agent_id, user, account)
