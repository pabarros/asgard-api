from typing import Dict
from pydantic import BaseModel
from pydantic.validators import dict_validator


class Model(BaseModel):
    errors: Dict[str, str] = {}

    def add_error(self, field_name, error_msg):
        self.errors[field_name] = error_msg
