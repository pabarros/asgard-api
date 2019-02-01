import os
from importlib import reload
from asynctest import TestCase, mock
from aioresponses import aioresponses
from tests.utils import get_fixture

import asgard.sdk.mesos
from asgard.backends.mesos import MesosBackend
import asgard.backends


class MesosBackendTest(TestCase):
    async def setUp(self):
        self.mesos_address = "http://10.0.0.1:5050"
        self.mesos_leader_ip_pactcher = mock.patch(
            "asgard.sdk.mesos.get_mesos_leader_address",
            mock.MagicMock(return_value=self.mesos_address),
        )
        self.mesos_leader_ip_pactcher.start()

        self.mesos_backend = MesosBackend()

    async def tearDown(self):
        mock.patch.stopall()

    async def test_get_agents_filtered_by_namespace(self):
        with mock.patch.dict(
            os.environ, HOLLOWMAN_MESOS_ADDRESS_0=self.mesos_address
        ), aioresponses(passthrough=["http://127.0.0.1"]) as rsps:
            rsps.get(
                f"{self.mesos_address}/redirect",
                status=301,
                headers={"Location": self.mesos_address},
            )
            rsps.get(
                f"{self.mesos_address}/slaves",
                payload=get_fixture("agents_multi_owner.json"),
                status=200,
            )
            agents = await self.mesos_backend.get_agents(namespace="asgard")
            self.assertEqual(4, len(agents))
            self.assertEqual(
                set(["asgard"]),
                set([agent.attributes["owner"] for agent in agents]),
            )

    async def test_get_agents_remove_unused_fields(self):
        with mock.patch.dict(
            os.environ, HOLLOWMAN_MESOS_ADDRESS_0=self.mesos_address
        ), aioresponses(passthrough=["http://127.0.0.1"]) as rsps:
            rsps.get(
                f"{self.mesos_address}/redirect",
                status=301,
                headers={"Location": self.mesos_address},
            )
            rsps.get(
                "http://10.0.0.1:5050/slaves",
                payload=get_fixture("agents_list_raw_fields.json"),
                status=200,
            )
            agents = await self.mesos_backend.get_agents(namespace="asgard")
            self.assertEqual(1, len(agents))
            self.assertEqual("asgard", agents[0].attributes["owner"])
