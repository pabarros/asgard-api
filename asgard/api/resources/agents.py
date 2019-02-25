from typing import List, Dict, Any
from pydantic import validator, BaseModel

from asgard.models import AgentFactory


class AgentsResource(BaseModel):
    agents: List[AgentFactory] = []
    stats: Dict[str, Any] = {}
