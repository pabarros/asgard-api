from enum import Enum
from typing import Optional, List

from asgard.models.base import BaseModel


class ContainerParameterSpec(BaseModel):
    type = "ASGARD"
    name: str
    value: str


class ContainerVolumeModes(str, Enum):
    RO = "RO"
    RW = "RW"


class ContainerVolumeSpec(BaseModel):
    type = "ASGARD"
    containerPath: str
    hostPath: str
    mode: ContainerVolumeModes = ContainerVolumeModes.RO
    persistent: bool = False
    external: bool = False


class ContainerPortProtocolTypes(str, Enum):
    TCP = "TCP"
    UDP = "UDP"


class ContainerPortSpec(BaseModel):
    type = "ASGARD"
    name: str
    containerPort: int
    protocol: ContainerPortProtocolTypes = ContainerPortProtocolTypes.TCP


class ContainerSpec(BaseModel):
    type = "ASGARD"
    image: str
    network: str
    parameters: Optional[List[ContainerParameterSpec]]
    privileged: bool = False
    pull_image: bool = True
    volumes: Optional[List[ContainerVolumeSpec]]
    ports: Optional[List[ContainerPortSpec]]
