from enum import Enum

from asgard.models.base import BaseModel


class ConstraintOperator(str, Enum):
    LIKE: str = "LIKE"


class ConstraintSpec(BaseModel):
    type = "ASGARD"
    label: str
    operator: ConstraintOperator
    value: str
