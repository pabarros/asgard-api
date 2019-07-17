from typing import Optional, List

from pydantic import BaseModel


class ChronosEnvSpec(BaseModel):
    key: str
    value: str


class ChronosContainerVolumeSpec(BaseModel):
    type = "CHRONOS"
    containerPath: str
    hostPath: str
    mode: str


class ChronosContainerParameterSpec(BaseModel):
    type = "CHRONOS"
    key: str
    value: str


class ChronosContainerSpec(BaseModel):
    type = "CHRONOS"
    image: str
    network: str
    parameters: Optional[List[ChronosContainerParameterSpec]]
    forcePullImage: bool = True
    volumes: Optional[List[ChronosContainerVolumeSpec]]

class ChronosFetchURLSpec(BaseModel):
    type = "CHRONOS"
    uri: str
    executable: bool = False
    cache: bool = False
    extract: bool = True


class ChronosJob(BaseModel):
    name: str
    command: Optional[str]
    arguments: Optional[List[str]]
    description: str
    shell: bool = False
    retries: int = 2
    disabled: bool = False
    concurrent: bool = False
    cpus: float
    mem: int
    disk: int
    schedule: str
    scheduleTimeZone: str
    environmentVariables: Optional[List[ChronosEnvSpec]]
    container: ChronosContainerSpec
    fetch: Optional[List[ChronosFetchURLSpec]]
    # constraints:
