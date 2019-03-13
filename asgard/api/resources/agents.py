from typing import Any, Dict, List

from pydantic import BaseModel, validator

from asgard.models import AgentFactory


class AgentsResource(BaseModel):
    agents: List[AgentFactory] = []
    stats: Dict[str, Any] = {}
