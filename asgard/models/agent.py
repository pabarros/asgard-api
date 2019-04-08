import abc
from typing import List

from asgard.models.app import App
from asgard.models.base import BaseModel, ModelFactory


class Agent(BaseModel, abc.ABC):
    def has_attribute(self, attr_name):
        return attr_name in self.attributes

    def _get_attribute_value(self, attr_name):
        return self.attributes[attr_name]

    def attr_has_value(self, attr_name, attr_value):
        return (
            self.has_attribute(attr_name)
            and self._get_attribute_value(attr_name) == attr_value
        )

    @abc.abstractmethod
    async def apps(self) -> List[App]:
        raise NotImplementedError

    @abc.abstractmethod
    async def calculate_stats(self):
        raise NotImplementedError


AgentFactory = ModelFactory(Agent)
