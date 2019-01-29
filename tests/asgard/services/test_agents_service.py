from asynctest import TestCase
from asynctest.mock import CoroutineMock

from asgard.services import AgentsService


class AgentsServicetTest(TestCase):
    async def setUp(self):
        self.agents_service = AgentsService()

    async def test_calls_backedn_passing_namespace(self):
        backend = CoroutineMock(get_agents=CoroutineMock())
        await self.agents_service.get_agents(namespace="dev", backend=backend)
        backend.get_agents.assert_awaited_with("dev")
