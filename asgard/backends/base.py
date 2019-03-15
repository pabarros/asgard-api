import abc
from typing import List, Optional

from asgard.models.agent import Agent
from asgard.models.app import App
from asgard.models.task import Task


class Backend(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    async def get_agents(self, namespace: str) -> List[Agent]:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_apps(self, namespace: str, agent_id: str) -> List[App]:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_agent_by_id(
        self, namespace: str, agent_id: str
    ) -> Optional[Agent]:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_tasks(
        self, namespace: str, agent_id: str, app_id: str
    ) -> List[Task]:
        raise NotImplementedError
