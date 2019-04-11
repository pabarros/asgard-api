from typing import Dict, Type

from pydantic import BaseModel as PydanticBaseModel

from asgard.backends.mesos.models.agent import MesosAgent as AsgardMesosAgent


class MesosAgent(PydanticBaseModel):
    id: str
    hostname: str
    port: int
    attributes: Dict[str, str]
    version: str
    active: bool
    used_resources: Dict[str, str]
    resources: Dict[str, str]

    def to_asgard_model(
        self, class_: Type[AsgardMesosAgent]
    ) -> AsgardMesosAgent:
        return class_(**self.dict())
