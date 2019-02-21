from typing import List, Dict, Any
from pydantic import validator

from asgard.services.models.agent import AgentFactory
from asgard.services.models import Model


class AgentsResource(Model):
    agents: List[AgentFactory] = []
    stats: Dict[str, Any] = {}
