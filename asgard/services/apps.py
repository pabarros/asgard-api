from typing import Optional

from asgard.backends.base import Orchestrator
from asgard.models.account import Account
from asgard.models.app import AppStats, App
from asgard.models.user import User


class AppsService:
    @staticmethod
    async def get_app_stats(
        app_id: str,
        timeframe: str,
        user: User,
        account: Account,
        orchestrator: Orchestrator,
    ) -> Optional[AppStats]:
        app = await AppsService.get_app_by_id(app_id, user, account)
        if app:
            return await orchestrator.get_app_stats(
                app, timeframe, user, account
            )
        raise NotImplementedError

    @staticmethod
    async def get_app_by_id(
        app_id: str, user: User, account: Account
    ) -> Optional[App]:
        pass
