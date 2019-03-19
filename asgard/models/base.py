from typing import Dict, Type

from pydantic import BaseModel as PydanticBaseModel
from sqlalchemy.ext.declarative import declarative_base


class BaseModel(PydanticBaseModel):
    type: str
    errors: Dict[str, str] = {}

    def add_error(self, field_name, error_msg):
        self.errors[field_name] = error_msg


BaseModelAlchemy = declarative_base()


def ModelFactory(subclass_marker: Type[BaseModel]):
    class _ModelFactory(PydanticBaseModel):
        def __new__(cls, *args, **kwargs) -> BaseModel:
            type_ = kwargs.pop("type")
            for subclass in subclass_marker.__subclasses__():
                if subclass.__fields__["type"].default == type_:
                    return subclass(*args, **kwargs)
            raise ValueError(
                f"'{type_}' is an invalid {subclass_marker} type. "
            )

    return _ModelFactory
