import abc
from .base import Model


class Task(Model, abc.ABC):
    _type: str

    @abc.abstractstaticmethod
    def transform_to_asgard_task_id(executor_id: str) -> str:
        raise NotImplementedError
