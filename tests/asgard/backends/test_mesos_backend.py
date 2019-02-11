import os
from asynctest import TestCase, mock, skip
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
                f"{self.mesos_address}/slaves",
                payload=get_fixture("agents_list_raw_fields.json"),
                status=200,
            )
            agents = await self.mesos_backend.get_agents(namespace="asgard")
            self.assertEqual(1, len(agents))
            self.assertEqual("asgard", agents[0].attributes["owner"])

    async def test_get_agent_by_id_returns_None_for_agent_in_another_namespace(
        self
    ):
        slave_id = "ead07ffb-5a61-42c9-9386-21b680597e6c-S0"
        with mock.patch.dict(
            os.environ, HOLLOWMAN_MESOS_ADDRESS_0=self.mesos_address
        ), aioresponses(passthrough=["http://127.0.0.1"]) as rsps:
            rsps.get(
                f"{self.mesos_address}/redirect",
                status=301,
                headers={"Location": self.mesos_address},
            )
            rsps.get(
                f"{self.mesos_address}/slaves?slave_id={slave_id}",
                payload=get_fixture("agents_multi_owner.json"),
                status=200,
            )
            agent = await self.mesos_backend.get_agent_by_id(
                namespace="dev",
                agent_id=slave_id,  # Agent from asgard-infra namespace
            )
            self.assertIsNone(agent)

    async def test_get_agent_by_id_return_None_if_agent_not_found(self):
        slave_id = "39e1a8e3-0fd1-4ba6-981d-e01318944957-S2"
        with mock.patch.dict(
            os.environ, HOLLOWMAN_MESOS_ADDRESS_0=self.mesos_address
        ), aioresponses(passthrough=["http://127.0.0.1"]) as rsps:
            rsps.get(
                f"{self.mesos_address}/redirect",
                status=301,
                headers={"Location": self.mesos_address},
            )
            rsps.get(
                f"{self.mesos_address}/slaves?slave_id={slave_id}",
                payload={"slaves": []},
                status=200,
            )
            agent = await self.mesos_backend.get_agent_by_id(
                namespace="dev",
                agent_id=slave_id,  # Agent from asgard-infra namespace
            )
            self.assertIsNone(agent)

    async def test_get_apps_returns_empty_list_if_agent_not_found(self):
        slave_id = "39e1a8e3-0fd1-4ba6-981d-e01318944957-S2"
        with mock.patch.dict(
            os.environ, HOLLOWMAN_MESOS_ADDRESS_0=self.mesos_address
        ), aioresponses(passthrough=["http://127.0.0.1"]) as rsps:
            rsps.get(
                f"{self.mesos_address}/redirect",
                status=301,
                headers={"Location": self.mesos_address},
            )
            rsps.get(
                f"{self.mesos_address}/slaves?slave_id={slave_id}",
                payload={"slaves": []},
                status=200,
            )
            apps = await self.mesos_backend.get_apps(
                namespace="dev", agent_id=slave_id
            )
            self.assertEqual(0, len(apps))

    async def test_get_apps_returns_empty_list_if_no_apps_running_on_agent(
        self
    ):
        slave_fixture = get_fixture("agents_multi_owner.json")
        slave = slave_fixture["slaves"][0]
        slave_id = slave["id"]
        slave_address = f"http://{slave['hostname']}:{slave['port']}"
        slave_namespace = slave["attributes"]["owner"]
        with mock.patch.dict(
            os.environ, HOLLOWMAN_MESOS_ADDRESS_0=self.mesos_address
        ), aioresponses(passthrough=["http://127.0.0.1"]) as rsps:
            rsps.get(
                f"{self.mesos_address}/redirect",
                status=301,
                headers={"Location": self.mesos_address},
            )
            rsps.get(
                f"{self.mesos_address}/slaves?slave_id={slave_id}",
                payload=slave_fixture,
                status=200,
            )
            rsps.get(f"{slave_address}/containers", payload=[], status=200)
            apps = await self.mesos_backend.get_apps(
                namespace=slave_namespace, agent_id=slave_id
            )
            self.assertEqual(0, len(apps))

    async def test_get_apps_returns_apps_running_on_agent(self):
        slave_fixture = get_fixture("agents_multi_owner.json")
        slave = slave_fixture["slaves"][0]
        slave_id = slave["id"]
        slave_address = f"http://{slave['hostname']}:{slave['port']}"
        slave_namespace = slave["attributes"]["owner"]
        with mock.patch.dict(
            os.environ, HOLLOWMAN_MESOS_ADDRESS_0=self.mesos_address
        ), aioresponses(passthrough=["http://127.0.0.1"]) as rsps:
            rsps.get(
                f"{self.mesos_address}/redirect",
                status=301,
                headers={"Location": self.mesos_address},
            )
            rsps.get(
                f"{self.mesos_address}/slaves?slave_id={slave_id}",
                payload=slave_fixture,
                status=200,
            )
            rsps.get(
                f"{slave_address}/containers",
                payload=get_fixture("agents_containers.json"),
                status=200,
            )
            apps = await self.mesos_backend.get_apps(
                namespace=slave_namespace, agent_id=slave_id
            )
            self.assertEqual(6, len(apps))

            expected_app_ids = [
                "infra/asgard/async-api",
                "captura/wetl/visitcentral",
                "portal/api",
                "captura/kirby/feeder",
                "infra/asgard/api",
                "infra/rabbitmq",
            ]
            self.assertEqual(expected_app_ids, [app.id for app in apps])

    async def test_get_tasks_from_app_zero_running_tasks(self):
        self.fail()

    async def test_get_tasks_from_app_not_in_same_namespace(self):
        self.fail()

    async def test_tasks_from_app_agent_not_found(self):
        """
        API do mesos retornoru {"slaves": []} quando buscamos pelo slave_id
        """
        self.fail()

    async def test_tasks_from_app_agent_connection_error(self):
        self.fail()

    async def test_get_tasks_from_app_some_tasks_running(self):
        self.fail()
