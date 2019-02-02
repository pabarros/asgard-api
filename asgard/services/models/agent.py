import abc
from asgard.services.models import Model


class Agent(Model, abc.ABC):
    _type: str = NotImplementedError

    def has_attribute(self, attr_name):
        return attr_name in self.attributes

    def _get_attribute_value(self, attr_name):
        return self.attributes[attr_name]

    def attr_has_value(self, attr_name, attr_value):
        return (
            self.has_attribute(attr_name)
            and self._get_attribute_value(attr_name) == attr_value
        )

    def filter_by_attrs(self):
        raise NotImplementedError


class AgentFactory(Model):
    def __new__(cls, *args, **kwargs) -> Agent:
        type_ = kwargs.pop("type")
        for subclass in Agent.__subclasses__():
            if subclass._type == type_:
                agent = subclass(*args, **kwargs)
                return agent
        raise ValueError(f"'{type_}' is an invalid agent type. ")
