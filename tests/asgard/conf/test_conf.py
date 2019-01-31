import asynctest
import os
from asynctest import mock
from importlib import reload


from asgard import conf


class AsgardConfTest(asynctest.TestCase):
    async def test_default_http_load_timeout_config_from_envs(self):
        with mock.patch.dict(
            os.environ,
            ASGARD_HTTP_CLIENT_CONNECT_TIMEOUT="10",
            ASGARD_HTTP_CLIENT_TOTAL_TIMEOUT="60",
        ):
            reload(conf)
            self.assertEqual(conf.ASGARD_HTTP_CLIENT_CONNECT_TIMEOUT, 10)
            self.assertEqual(conf.ASGARD_HTTP_CLIENT_TOTAL_TIMEOUT, 60)

    async def test_default_http_load_timeout_values(self):
        reload(conf)
        self.assertEqual(conf.ASGARD_HTTP_CLIENT_CONNECT_TIMEOUT, 1)
        self.assertEqual(conf.ASGARD_HTTP_CLIENT_TOTAL_TIMEOUT, 30)
