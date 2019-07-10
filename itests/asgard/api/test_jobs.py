from asgard.api import jobs
from asgard.app import app
from asgard.models.job import ScheduledJob
from itests.util import BaseTestCase


class JobsEndpointTestCase(BaseTestCase):
    async def setUp(self):
        await super(JobsEndpointTestCase, self).setUp()
        self.client = await self.aiohttp_client(app)

    async def tearDown(self):
        await super(JobsEndpointTestCase, self).tearDown()

    async def test_jobs_post_new_job_required_fields(self):

        container_spec = {"image": "alpine:3", "network": "BRIDGE"}
        schedule_spec = {
            "value": "20190811T2100+00:00/R",
            "tz": "America/Sao_Paulo",
        }

        required_fields_scheduled_job = {
            "id": "my-sheduled-app",
            "cpus": 5.0,
            "mem": 512,
            "container": {**container_spec},
            "schedule": schedule_spec,
            "description": "A Scheduled Task",
        }
        resp = await self.client.post(
            "/jobs", headers={}, json={**required_fields_scheduled_job}
        )
        resp_data = await resp.json()
        scheduled_job = ScheduledJob(**resp_data)
        self.assertEqual(scheduled_job.dict(), resp_data)
