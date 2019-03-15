import abc

from .base import BaseModel, ModelFactory


class App(BaseModel, abc.ABC):
    @abc.abstractstaticmethod
    def transform_to_asgard_app_id(name: str) -> str:
        raise NotImplementedError


AppFactory = ModelFactory(App)
