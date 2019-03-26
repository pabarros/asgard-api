from typing import List, Optional

from asgard.backends.base import AppsBackend
from asgard.models.account import Account
from asgard.models.app import App
from asgard.models.task import Task
from asgard.models.user import User


class MarathonAppsBackend(AppsBackend):
    async def get_apps_definition(
        self, user: User, account: Account
    ) -> List[App]:
        raise NotImplementedError

    async def get_by_id(
        self, app_id: str, user: User, account: Account
    ) -> Optional[App]:
        raise NotImplementedError

    async def get_tasks(self, app: App) -> Optional[Task]:
        raise NotImplementedError
