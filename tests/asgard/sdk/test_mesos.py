import os
from asynctest import TestCase, mock
from aioresponses import aioresponses

from asgard.sdk.mesos import leader_address


class TestMesos(TestCase):
    async def test_get_mesos_leader_ip(self):
        mesos_addresses = [
            "http://10.0.2.1:5050",
            "http://10.0.2.3:5050",
            "http://10.0.2.2:5050",
        ]
        with mock.patch.dict(
            os.environ,
            HOLLOWMAN_MESOS_ADDRESS_0=mesos_addresses[0],
            HOLLOWMAN_MESOS_ADDRESS_1=mesos_addresses[1],
            HOLLOWMAN_MESOS_ADDRESS_2=mesos_addresses[2],
            ASGARD_HTTP_CLIENT_TOTAL_TIMEOUT="1",
            ASGARD_HTTP_CLIENT_CONNECT_TIMEOUT="1",
        ), aioresponses(
            passthrough=["http://127.0.0.1", "http://10.0.2.1:5050"]
        ) as rsps:
            rsps.get(
                mesos_addresses[1] + "/redirect",
                status=302,
                body="",
                headers={"Location": "//10.0.2.2:5050"},
            )
            mesos_leader_ip = await leader_address()

            self.assertEqual("http://10.0.2.2:5050", mesos_leader_ip)
