from typing import List, Optional

from asgard.models.base import BaseModel
from asgard.models.spec.constraint import ConstraintSpec
from asgard.models.spec.container import ContainerSpec
from asgard.models.spec.env import EnvSpec
from asgard.models.spec.fetch import FetchURISpec
from asgard.models.spec.schedule import ScheduleSpec


class App(BaseModel):
    type: str = "ASGARD"
    id: str
    command: Optional[List[str]]
    arguments: Optional[List[str]]
    cpus: float
    mem: int
    disk: int = 0
    container: ContainerSpec
    env: Optional[List[EnvSpec]]
    constraints: Optional[List[ConstraintSpec]]
    fetch: Optional[List[FetchURISpec]]


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
