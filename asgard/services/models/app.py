import abc
from asgard.services.models import Model


class App(Model, abc.ABC):
    _type: str


class AppFactory(Model):
    def __new__(cls, *args, **kwargs) -> App:
        type_ = kwargs.pop("type")
        for subclass in App.__subclasses__():
            if subclass._type == type_:
                agent = subclass(*args, **kwargs)
                return agent
        raise ValueError(f"'{type_}' is an invalid App type. ")
