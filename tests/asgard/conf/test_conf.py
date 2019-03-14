import os
from importlib import reload

import asynctest
from asynctest import mock

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

    async def test_default_task_fileread_max_length(self):
        reload(conf)
        self.assertEqual(conf.TASK_FILEREAD_MAX_OFFSET, 52_428_800)

    async def test_task_fileread_max_length_is_converted_to_int(self):
        with mock.patch.dict(
            os.environ, ASGARD_TASK_FILEREAD_MAX_OFFSET="1024"
        ):
            reload(conf)
        self.assertEqual(conf.TASK_FILEREAD_MAX_OFFSET, 1024)
