from typing import List

from pydantic import BaseModel

from asgard.models.app import AppFactory, AppStats


class AppsResource(BaseModel):
    apps: List[AppFactory] = []


class AppStatsResource(BaseModel):
    stats = AppStats
