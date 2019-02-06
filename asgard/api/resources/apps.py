from typing import List
from asgard.services.models import Model
from asgard.services.models.app import AppFactory


class AppsResource(Model):
    apps: List[AppFactory] = []
