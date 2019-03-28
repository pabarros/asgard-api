import abc

from .base import BaseModel, ModelFactory


class App(BaseModel, abc.ABC):
    id: str

    @abc.abstractstaticmethod
    def transform_to_asgard_app_id(name: str) -> str:
        raise NotImplementedError


class AppStats(BaseModel):
    type: str = "ASGARD"
    cpu_pct: str
    ram_pct: str
    timeframe: str


AppFactory = ModelFactory(App)
