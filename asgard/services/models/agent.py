from typing import Dict, List, Union
from asgard.services.models import Model
from abc import ABC, abstractmethod
from pydantic.validators import dict_validator


class Agent(Model):
    type: str

    def has_attribute(self, attr_name):
        return attr_name in self.attributes

    def _get_attribute_value(self, attr_name):
        return self.attributes[attr_name]

    def attr_has_value(self, attr_name, attr_value):
        return (
            self.has_attribute(attr_name)
            and self._get_attribute_value(attr_name) == attr_value
        )

    def filter_by_attrs(self):
        raise NotImplementedError
