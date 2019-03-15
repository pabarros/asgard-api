import abc

from .base import BaseModel


class Task(BaseModel, abc.ABC):
    @abc.abstractstaticmethod
    def transform_to_asgard_task_id(executor_id: str) -> str:
        raise NotImplementedError
