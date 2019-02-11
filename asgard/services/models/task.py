import abc
from asgard.services.models import Model


class Task(Model, abc.ABC):
    _type: str


class AppFactory(Model):
    def __new__(cls, *args, **kwargs) -> Task:
        type_ = kwargs.pop("type")
        for subclass in Task.__subclasses__():
            if subclass._type == type_:
                agent = subclass(*args, **kwargs)
                return agent
        raise ValueError(f"'{type_}' is an invalid Task type. ")
