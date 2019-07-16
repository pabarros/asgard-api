from asgard.clients.chronos.models.job import ChronosJob
from asgard.http.client import http_client


class ChronosClient:
    def __init__(self, url: str) -> None:
        self.address = url

    async def get_job_by_id(self, job_id: str) -> ChronosJob:
        async with http_client as client:
            resp = await client.get(f"{self.address}/v1/scheduler/job/{job_id}")
            data = await resp.json()
            return ChronosJob(**data)
        return None
