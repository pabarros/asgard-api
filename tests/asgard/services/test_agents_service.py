from asynctest import TestCase
from asynctest.mock import Mock

from asgard.backends.base import Orchestrator
from asgard.models.account import Account
from asgard.models.user import User
from asgard.services import AgentsService
from itests.util import ACCOUNT_DEV_DICT, USER_WITH_MULTIPLE_ACCOUNTS_DICT


class AgentsServicetTest(TestCase):
    async def setUp(self):
        self.backend_mock = Mock(spec=Orchestrator)
        self.agents_service = AgentsService()
        self.account = Account(**ACCOUNT_DEV_DICT)
        self.user = User(**USER_WITH_MULTIPLE_ACCOUNTS_DICT)

    async def test_get_agents_calls_backend_passing_right_params(self):
        await self.agents_service.get_agents(
            self.user, self.account, self.backend_mock
        )
        self.backend_mock.get_agents.assert_awaited_with(
            self.user, self.account
        )

    async def test_get_apps_calls_backend_passing_right_params(self):
        agent_mock = Mock()
        user_mock = Mock()
        await self.agents_service.get_apps_running_for_agent(
            user_mock, agent_mock, backend=self.backend_mock
        )
        self.backend_mock.get_apps_running_for_agent.assert_awaited_with(
            user_mock, agent_mock
        )

    async def test_get_agent_by_id_call_backend_with_correct_params(self):
        agent_mock = Mock()
        user_mock = Mock()
        agent_id = "id"
        await self.agents_service.get_agent_by_id(
            agent_id, user_mock, agent_mock, backend=self.backend_mock
        )
        self.backend_mock.get_agent_by_id.assert_awaited_with(
            agent_id, user_mock, agent_mock
        )
