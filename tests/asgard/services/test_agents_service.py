from asynctest import TestCase
from asynctest.mock import Mock

from asgard.backends.base import Backend
from asgard.services import AgentsService


class AgentsServicetTest(TestCase):
    async def setUp(self):
        self.backend_mock = Mock(spec=Backend)
        self.agents_service = AgentsService()

    async def test_get_agents_calls_backend_passing_right_params(self):
        await self.agents_service.get_agents(
            namespace="dev", backend=self.backend_mock
        )
        self.backend_mock.get_agents.assert_awaited_with("dev")

    async def test_get_apps_calls_backend_passing_right_params(self):
        agent_id = "fa8dd968-40c9-4179-9b1f-38b56341a2a4-S0"
        await self.agents_service.get_apps(
            namespace="dev", agent_id=agent_id, backend=self.backend_mock
        )
        self.backend_mock.get_apps.assert_awaited_with("dev", agent_id)

    async def test_get_tasks_calls_backend_passing_right_parameters(self):
        agent_id = "fa8dd968-40c9-4179-9b1f-38b56341a2a4-S0"
        app_id = "/apps/http/myapp"
        await self.agents_service.get_tasks(
            namespace="dev",
            agent_id=agent_id,
            app_id=app_id,
            backend=self.backend_mock,
        )
        self.backend_mock.get_tasks.assert_awaited_with("dev", agent_id, app_id)
