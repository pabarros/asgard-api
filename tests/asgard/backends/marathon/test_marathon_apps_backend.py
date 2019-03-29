from aioresponses import aioresponses
from asynctest import TestCase, mock
from freezegun import freeze_time

from asgard.backends.marathon.impl import MarathonAppsBackend
from asgard.backends.mesos.models.app import MesosApp
from asgard.models.account import Account
from asgard.models.app import AppStats
from asgard.models.user import User
from itests.util import USER_WITH_MULTIPLE_ACCOUNTS_DICT, ACCOUNT_DEV_DICT
from tests.utils import (
    TEST_MESOS_ADDRESS,
    build_mesos_cluster,
    add_agent_task_stats,
)


class MarathonAppsBackendTest(TestCase):
    async def setUp(self):

        self.user = User(**USER_WITH_MULTIPLE_ACCOUNTS_DICT)
        self.account = Account(**ACCOUNT_DEV_DICT)
        self.apps_backend = MarathonAppsBackend()

    @freeze_time("2019-03-29")
    async def test_get_app_stats_has_some_data(self):
        with aioresponses(passthrough=["http://127.0.0.1"]) as rsps:
            agent_id = "ead07ffb-5a61-42c9-9386-21b680597e6c-S0"
            build_mesos_cluster(rsps, agent_id)
            add_agent_task_stats(
                rsps, agent_id, index_name="asgard-app-stats-2019-03-29-*"
            )
            stats = await self.apps_backend.get_app_stats(
                MesosApp(id="infra-asgard-api"), self.user, self.account
            )
            self.assertEqual(AppStats(cpu_pct="4.51", ram_pct="22.68"), stats)
