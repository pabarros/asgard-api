
from importlib import reload
import asynctest
from asgard import conf
from asgard import app

class AsgardAppTest(asynctest.TestCase):

    async def test_load_with_conf_values(self):
        with asynctest.mock.patch.multiple(conf, ASGARD_RABBITMQ_HOST="10.0.0.1", \
ASGARD_RABBITMQ_USER="user1",\
ASGARD_RABBITMQ_PASS="pass1",\
                                           ASGARD_RABBITMQ_PREFETCH=64):
            reload(app)
            self.assertEqual("10.0.0.1", app.app.host)
            self.assertEqual("user1", app.app.user)
            self.assertEqual("pass1", app.app.password)
            self.assertEqual(64, app.app.prefetch_count)
