from typing import List, Optional

from aioelasticsearch import Elasticsearch
from elasticsearch_dsl import Search

from asgard.backends.base import AppsBackend
from asgard.conf import settings
from asgard.elasticsearch.models.search import AppsStatsResult
from asgard.models.account import Account
from asgard.models.app import App, AppStats
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

    async def get_app_stats(
        self, app: App, timeframe: str, user: User, account: Account
    ) -> AppStats:
        es = Elasticsearch([settings.STATS_API_URL])
        query = Search(index="index").query("match", appname="name")
        dict_query = query.to_dict()
        index_name = f"{account.namespace}-{app.id.replace('/', '-')}"
        result = AppsStatsResult(
            **await es.search(
                index=f"asgard-app-stats-{index_name}-*", body=dict_query
            )
        )
        return AppStats(
            cpu_pct=str(result.aggregations.avg_cpu_pct.value),
            ram_pct=str(result.aggregations.avg_mem_pct.value),
            timeframe=timeframe,
        )
