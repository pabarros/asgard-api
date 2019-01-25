from asgard.backends.base import Backend

from asgard.sdk.mesos import get_mesos_leader_address
from asgard.http.client import http_client


class MesosBackend(Backend):
    async def get_agents(self, namespace: str):
        agents_url = f"{get_mesos_leader_address()}/slaves"
        async with http_client.get(agents_url) as response:
            data = await response.json()
            for agent in data["slaves"]:
                agent.pop("pid", None)
                agent.pop("registered_time", None)
                agent.pop("offered_resources", None)
                agent.pop("reserved_resources", None)
                agent.pop("unreserved_resources", None)
                agent.pop("capabilities", None)
                agent.pop("reserved_resources_full", None)
                agent.pop("unreserved_resources_full", None)
                agent.pop("used_resources_full", None)
                agent.pop("offered_resources_full", None)
        return {"agents": data["slaves"]}
