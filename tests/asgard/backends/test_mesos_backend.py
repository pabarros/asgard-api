from importlib import reload
from asynctest import TestCase, mock
from aioresponses import aioresponses
from tests.utils import get_fixture

import asgard.sdk.mesos
from asgard.backends.mesos import MesosBackend
import asgard.backends


class MesosBackendTest(TestCase):
    async def setUp(self):
        self.mesos_leader_ip_pactcher = mock.patch(
            "asgard.sdk.mesos.get_mesos_leader_address",
            mock.MagicMock(return_value="http://10.0.0.1:5050"),
        )
        self.mesos_leader_ip_pactcher.start()

        self.mesos_backend = MesosBackend()

    async def tearDown(self):
        mock.patch.stopall()

    async def test_get_agents_filtered_by_namespace(self):
        with aioresponses() as rsps:
            rsps.get(
                "http://10.0.0.1:5050/slaves",
                payload=get_fixture("agents_multi_owner.json"),
                status=200,
            )
            agents_data = await self.mesos_backend.get_agents(
                namespace="asgard"
            )
            self.assertEqual(4, len(agents_data["agents"]))
            self.assertEqual(
                set(["asgard"]),
                set(
                    [
                        agent["attributes"]["owner"]
                        for agent in agents_data["agents"]
                    ]
                ),
            )

    async def test_get_agents_remove_unused_fields(self):
        with aioresponses() as rsps:
            rsps.get(
                "http://10.0.0.1:5050/slaves",
                payload=get_fixture("agents_list_raw_fields.json"),
                status=200,
            )
            agents_data = await self.mesos_backend.get_agents(
                namespace="asgard"
            )
            self.assertEqual(1, len(agents_data["agents"]))
            self.assertEqual(
                "asgard", agents_data["agents"][0]["attributes"]["owner"]
            )
            self.assertEqual(
                set(
                    [
                        "reregistered_time",
                        "active",
                        "version",
                        "id",
                        "used_resources",
                        "hostname",
                        "attributes",
                        "resources",
                        "port",
                    ]
                ),
                set(agents_data["agents"][0].keys()),
            )
