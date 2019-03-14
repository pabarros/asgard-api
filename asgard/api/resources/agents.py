from typing import Any, Dict, List

from pydantic import BaseModel

from asgard.models.agent import AgentFactory


class AgentsResource(BaseModel):
    agents: List[AgentFactory] = []
    stats: Dict[str, Any] = {}
