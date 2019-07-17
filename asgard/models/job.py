from typing import List, Optional, Dict

from asgard.models.base import BaseModel
from asgard.models.spec.constraint import ConstraintSpec
from asgard.models.spec.container import ContainerSpec
from asgard.models.spec.env import EnvSpec
from asgard.models.spec.fetch import FetchURLSpec
from asgard.models.spec.schedule import ScheduleSpec


class App(BaseModel):
    id: Optional[str]
    command: Optional[str]
    arguments: Optional[List[str]]
    cpus: float
    mem: int
    disk: int = 0
    container: ContainerSpec
    env: Optional[EnvSpec]
    constraints: Optional[ConstraintSpec]
    fetch: Optional[List[FetchURLSpec]]


class ScheduledJob(App):
    """
    Modelo que representa uma tarefa agendada, que pode
    rodar em um intervalo de tempo qualquer.
    """

    description: str
    shell: bool = False
    retries: int = 2
    enabled: bool = True
    concurrent: bool = False
    schedule: ScheduleSpec
