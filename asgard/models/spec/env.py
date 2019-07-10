from asgard.models.base import BaseModel


class EnvSpec(BaseModel):
    name: str
    value: str
