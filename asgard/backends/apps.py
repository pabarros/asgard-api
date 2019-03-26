from typing import Optional, List

from asgard.models.account import Account
from asgard.models.app import App
from asgard.models.user import User


class AppsBackend:
    async def get_app_stats(
        self, app_id: str, timeframe: str, user: User, account: Account
    ) -> Optional[App]:
        """
        Retorna os dados de uso de CPU e RAM da app `app_id`, no período `timeframe`.
        A app é buscada na conta `account`, passada como parametro.
        `timeframe` é uma string no formato: 30m, 20m, etc.
        """
        pass

    async def get_apps(self, user: User, account: Account) -> List[App]:
        pass

    async def get_app_by_id(
        self, app_id: str, user: User, account: Account
    ) -> Optional[App]:
        pass
