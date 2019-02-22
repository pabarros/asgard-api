from typing import List

from asgard.models import Model
from asgard.models import AppFactory


class AppsResource(Model):
    apps: List[AppFactory] = []
