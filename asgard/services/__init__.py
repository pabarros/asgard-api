from typing import List
from asgard.backends.base import Backend

from asgard.services.models.agent import Agent


class AgentsService:
    async def get_agents(self, namespace: str, backend: Backend) -> List[Agent]:
        return await backend.get_agents(namespace)


agents_service = AgentsService()
