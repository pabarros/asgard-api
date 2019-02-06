from typing import List


from asgard.services.models.agent import Agent
from asgard.services.models.app import App


class AgentsService:
    async def get_agents(
        self, namespace: str, backend: "asgard.backends.base.Backend"
    ) -> List[Agent]:
        return await backend.get_agents(namespace)

    async def get_apps(
        self,
        namespace: str,
        agent_id: str,
        backend: "asgard.backends.base.Backend",
    ) -> List[App]:
        return await backend.get_apps(namespace, agent_id)
