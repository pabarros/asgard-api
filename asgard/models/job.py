from enum import Enum
from typing import List, Optional

from pydantic import validator

from asgard.models.base import BaseModel


class FetchURI(BaseModel):
    uri: str
    extract: bool = True
    executable: bool = False
    cache: bool = False


class EnvSpec(BaseModel):
    name: str
    value: str


class ConstraintOperator(str, Enum):
    LIKE: str = "LIKE"


class ConstraintSpec(BaseModel):
    type = "ASGARD"
    label: str
    operator: ConstraintOperator
    value: str


class ScheduledJob(BaseModel):
    """
    Modelo que representa uma tarefa agendada, que pode
    rodar em um intervalo de tempo qualquer.
    """

    type: str = "ASGARD"
    name: str
    description: str
    command: Optional[List[str]]
    arguments: Optional[List[str]]
    shell: bool = False
    retries: int = 2
    cpus: float
    mem: int
    disk: int = 0
    enabled: bool = True
    concurrent: bool = False
    fetch: Optional[List[FetchURI]]
    env: Optional[List[EnvSpec]]
    constraints: Optional[List[ConstraintSpec]]
