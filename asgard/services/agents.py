from typing import List

from asgard.models import Agent, App, Task


class AgentsService:
    async def get_agents(self, namespace: str, backend) -> List[Agent]:
        return await backend.get_agents(namespace)

    async def get_apps(
        self, namespace: str, agent_id: str, backend
    ) -> List[App]:
        return await backend.get_apps(namespace, agent_id)

    async def get_tasks(
        self, namespace: str, agent_id: str, app_id: str, backend
    ) -> List[Task]:
        return await backend.get_tasks(namespace, agent_id, app_id)
