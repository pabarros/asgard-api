from typing import List

from asgard.services.models.agent import AgentFactory
from asgard.services.models import Model


class AgentsResource(Model):
    agents: List[AgentFactory] = []
