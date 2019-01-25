from typing import Type
from asgard.backends.base import Backend


class AgentsService:
    async def get_agents(self, namespace: str, backend: Backend):
        return await backend.get_agents(namespace)


agents_service = AgentsService()
