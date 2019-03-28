from aioresponses import aioresponses
from asynctest import TestCase, mock
from tests.utils import (
    TEST_MESOS_ADDRESS,
    build_mesos_cluster,
    add_agent_task_stats,
)

from asgard.backends.marathon.impl import MarathonAppsBackend
from asgard.backends.mesos.models.app import MesosApp
from asgard.models.account import Account
from asgard.models.app import AppStats
from asgard.models.user import User
from itests.util import USER_WITH_MULTIPLE_ACCOUNTS_DICT, ACCOUNT_DEV_DICT


class MarathonAppsBackendTest(TestCase):
    async def setUp(self):

        self.user = User(**USER_WITH_MULTIPLE_ACCOUNTS_DICT)
        self.account = Account(**ACCOUNT_DEV_DICT)
        self.apps_backend = MarathonAppsBackend()

    async def test_get_app_stats_has_some_data(self):
        with aioresponses(passthrough=["http://127.0.0.1"]) as rsps:
            agent_id = "ead07ffb-5a61-42c9-9386-21b680597e6c-S0"
            build_mesos_cluster(rsps, agent_id)
            add_agent_task_stats(rsps, agent_id)
            stats = await self.apps_backend.get_app_stats(
                MesosApp(id="infra-asgard-api"), "30m", self.user, self.account
            )
            self.assertEqual(
                AppStats(
                    cpu_pct="4.50619298487354",
                    ram_pct="22.6756985018591",
                    timeframe="30m",
                ),
                stats,
            )

    async def test_get_app_stats_no_data(self):
        """
        No resultado do ES, temos um campo: `{"hits": "total": 0, ...}`
        Esse campo, quando for `0`, não tivemos resultado. Essa é a indicação
        de que o resultado do `apps_backend.get_app_stats()` será `None`.
        """
        self.fail()
