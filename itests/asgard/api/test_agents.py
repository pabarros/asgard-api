from itests.util import BaseTestCase
from tests.utils import get_fixture
from importlib import reload
from asynctest import mock, skip
from asynctest.mock import CoroutineMock
import os

from asgard.app import app
from aioresponses import aioresponses

from asgard.api import agents


class AgentsApiEndpointTest(BaseTestCase):
    async def setUp(self):
        await super(AgentsApiEndpointTest, self).setUp()
        self.client = await self.aiohttp_client(app)
        self.mesos_address = "http://10.0.0.1:5050"

    async def tearDown(self):
        await super(AgentsApiEndpointTest, self).tearDown()

    async def test_agents_list_should_return_only_agents_from_specific_account(
        self
    ):
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
                status=200,
                payload=get_fixture("agents_multi_owner.json"),
            )
            resp = await self.client.get(
                "/agents",
                headers={
                    "Authorization": "Token 69ed620926be4067a36402c3f7e9ddf0"
                },
            )
            self.assertEqual(200, resp.status)
            data = await resp.json()
            self.assertEqual(1, len(data["agents"]))
            self.assertEqual(
                set(["dev"]),
                set([agent["attributes"]["owner"] for agent in data["agents"]]),
            )
            self.assertEqual(
                "ead07ffb-5a61-42c9-9386-21b680597e6c-S44",
                data["agents"][0]["id"],
            )
