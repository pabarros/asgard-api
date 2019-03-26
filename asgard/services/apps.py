from typing import Optional

from asgard.backends.apps import AppsBackend
from asgard.models.account import Account
from asgard.models.app import AppStats
from asgard.models.user import User


class AppsService:
    @staticmethod
    async def get_app_stats(
        app_id: str,
        timeframe: str,
        user: User,
        account: Account,
        backend: AppsBackend,
    ) -> Optional[AppStats]:
        return await backend.get_app_stats(app_id, timeframe, user, account)
