from typing import Dict, Type
from pydantic import BaseModel as PydanticBaseModel


class Model(PydanticBaseModel):
    errors: Dict[str, str] = {}

    def add_error(self, field_name, error_msg):
        self.errors[field_name] = error_msg


class BaseModel(PydanticBaseModel):
    type: str


def ModelFactory(subclass_marker):
    class _ModelFactory:
        def __new__(cls, *args, **kwargs):
            type_ = kwargs.pop("type")
            for subclass in subclass_marker.__subclasses__():
                if subclass.__fields__["type"].default == type_:
                    return subclass(*args, **kwargs)
            raise ValueError(f"'{type_}' is an invalid {subclass_marker} type. ")

    return _ModelFactory
