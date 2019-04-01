import os

from aioresponses import aioresponses
from asynctest import TestCase, mock

from asgard.sdk.mesos import leader_address
from tests.conf import TEST_LOCAL_AIOHTTP_ADDRESS, TEST_MESOS_ADDRESS


class TestMesos(TestCase):
    async def test_get_mesos_leader_ip(self):
        mesos_addresses = [
            TEST_MESOS_ADDRESS,
            "http://10.0.2.3:5050",
            "http://10.0.2.2:5050",
        ]
        with mock.patch.dict(
            os.environ,
            HOLLOWMAN_MESOS_ADDRESS_0=mesos_addresses[0],
            HOLLOWMAN_MESOS_ADDRESS_1=mesos_addresses[1],
            HOLLOWMAN_MESOS_ADDRESS_2=mesos_addresses[2],
        ), aioresponses(
            passthrough=[TEST_LOCAL_AIOHTTP_ADDRESS, TEST_MESOS_ADDRESS]
        ) as rsps:
            rsps.get(
                mesos_addresses[1] + "/redirect",
                status=302,
                body="",
                headers={"Location": TEST_MESOS_ADDRESS},
            )
            mesos_leader_ip = await leader_address()

            self.assertEqual(TEST_MESOS_ADDRESS, mesos_leader_ip)
