from asynctest import skip

from itests.util import BaseTestCase


@skip("Future")
class AppStatsTest(BaseTestCase):
    async def test_apps_stats_empty_stats_for_timeperiod(self):
        self.fail()

    async def test_apps_stats_app_not_found(self):
        self.fail()

    async def test_apps_stats_return_stats_for_timeframe(self):
        self.fail()
