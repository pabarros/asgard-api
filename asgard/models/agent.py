from typing import List
import abc
from .base import BaseModel, ModelFactory

from asgard.models import App


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
    def filter_by_attrs(self, attrs_kv):
        raise NotImplementedError

    @abc.abstractmethod
    async def apps(self) -> List[App]:
        raise NotImplementedError

    @abc.abstractmethod
    async def calculate_stats(self):
        raise NotImplementedError


AgentFactory = ModelFactory(Agent)
