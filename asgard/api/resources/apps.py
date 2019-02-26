from typing import List

from pydantic import BaseModel

from asgard.models import AppFactory


class AppsResource(BaseModel):
    apps: List[AppFactory] = []
