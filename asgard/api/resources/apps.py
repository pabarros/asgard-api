from typing import List

from pydantic import BaseModel

from asgard.models.app import AppFactory


class AppsResource(BaseModel):
    apps: List[AppFactory] = []
