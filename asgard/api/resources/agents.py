from typing import List, Dict, Any
from pydantic import validator

from asgard.models import AgentFactory
from asgard.models import Model


class AgentsResource(Model):
    agents: List[AgentFactory] = []
    stats: Dict[str, Any] = {}
