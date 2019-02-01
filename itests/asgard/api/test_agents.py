from itests.util import BaseTestCase
from tests.utils import get_fixture
from importlib import reload
from asynctest import mock, skip
from asynctest.mock import CoroutineMock
import os

from asgard.app import app
from aioresponses import aioresponses
from hollowman.models import User, Account, UserHasAccount

from asgard.api import agents


class AgentsApiEndpointTest(BaseTestCase):
    async def setUp(self):
        await super(AgentsApiEndpointTest, self).setUp()
        self.client = await self.aiohttp_client(app)
        self.mesos_address = "http://10.0.0.1:5050"
        self.user_auth_key = "c0c0b73b18864550a3e3b93a59c4b7d8"

    def _mock_mesos_return_data(self, rsps):
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

    def _prepare_additional_fixture_data(self):
        self.pg_data_mocker.add_data(
            User,
            ["id", "tx_name", "tx_email", "tx_authkey"],
            [
                [
                    128,
                    "User for Infra Account",
                    "user-infra@host.com",
                    self.user_auth_key,
                ]
            ],
        )

        self.pg_data_mocker.add_data(
            Account,
            ["id", "name", "namespace", "owner"],
            [[40, "Dev Team", "asgard-infra", "company"]],
        )

        self.pg_data_mocker.add_data(
            UserHasAccount, ["id", "user_id", "account_id"], [[50, 128, 40]]
        )

    async def tearDown(self):
        await super(AgentsApiEndpointTest, self).tearDown()

    async def test_agents_list_should_return_only_agents_from_specific_account(
        self
    ):
        with mock.patch.dict(
            os.environ, HOLLOWMAN_MESOS_ADDRESS_0=self.mesos_address
        ), aioresponses(passthrough=["http://127.0.0.1"]) as rsps:
            self._mock_mesos_return_data(rsps)
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

    async def test_agents_with_attrs_empty_response(self):
        self._prepare_additional_fixture_data()
        await self.pg_data_mocker.create()

        with mock.patch.dict(
            os.environ, HOLLOWMAN_MESOS_ADDRESS_0=self.mesos_address
        ), aioresponses(passthrough=["http://127.0.0.1"]) as rsps:
            self._mock_mesos_return_data(rsps)
            resp = await self.client.get(
                "/agents/with-attrs?tag1=not-found",
                headers={"Authorization": f"Token {self.user_auth_key}"},
            )
            self.assertEqual(200, resp.status)
            data = await resp.json()
            self.assertEqual({"agents": []}, data)

    async def test_agents_with_atrrs_one_attr_filter(self):
        self._prepare_additional_fixture_data()
        await self.pg_data_mocker.create()

        with mock.patch.dict(
            os.environ, HOLLOWMAN_MESOS_ADDRESS_0=self.mesos_address
        ), aioresponses(passthrough=["http://127.0.0.1"]) as rsps:
            self._mock_mesos_return_data(rsps)
            resp = await self.client.get(
                "/agents/with-attrs?workload=general",
                headers={"Authorization": f"Token {self.user_auth_key}"},
            )
            self.assertEqual(200, resp.status)
            data = await resp.json()
            self.assertEqual(2, len(data["agents"]))
            self.assertEqual(
                "ead07ffb-5a61-42c9-9386-21b680597e6c-S0",
                data["agents"][0]["id"],
            )
            self.assertEqual(
                "ead07ffb-5a61-42c9-9386-21b680597e6c-S3",
                data["agents"][1]["id"],
            )

    async def test_agents_with_atrrs_two_attrs_filter(self):
        self._prepare_additional_fixture_data()
        await self.pg_data_mocker.create()

        with mock.patch.dict(
            os.environ, HOLLOWMAN_MESOS_ADDRESS_0=self.mesos_address
        ), aioresponses(passthrough=["http://127.0.0.1"]) as rsps:
            self._mock_mesos_return_data(rsps)
            resp = await self.client.get(
                "/agents/with-attrs?workload=general&dc=gcp",
                headers={"Authorization": f"Token {self.user_auth_key}"},
            )
            self.assertEqual(200, resp.status)
            data = await resp.json()
            self.assertEqual(1, len(data["agents"]))
            self.assertEqual(
                "ead07ffb-5a61-42c9-9386-21b680597e6c-S0",
                data["agents"][0]["id"],
            )
