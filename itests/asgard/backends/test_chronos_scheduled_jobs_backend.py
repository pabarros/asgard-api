import aiohttp
from asynctest import TestCase
from asynctest.mock import CoroutineMock

from asgard.backends.chronos.impl import ChronosScheduledJobsBackend
from asgard.clients.chronos import ChronosClient
from asgard.conf import settings
from asgard.http.client import http_client
from asgard.models.account import Account
from asgard.models.user import User
from itests.util import USER_WITH_MULTIPLE_ACCOUNTS_DICT, ACCOUNT_DEV_DICT
from tests.utils import with_json_fixture


class ChronosScheduledJobsBackendTest(TestCase):
    async def setUp(self):
        self.backend = ChronosScheduledJobsBackend()

    async def test_get_job_by_id_job_not_found(self):
        job_id = "job-not-found"
        user = User(**USER_WITH_MULTIPLE_ACCOUNTS_DICT)
        account = Account(**ACCOUNT_DEV_DICT)
        job = await self.backend.get_job_by_id(job_id, user, account)
        self.assertIsNone(job)

    async def test_add_namespace_to_job_name(self):
        self.backend.client = CoroutineMock(spec=ChronosClient)
        self.backend.client.get_job_by_id.return_value = None

        user = User(**USER_WITH_MULTIPLE_ACCOUNTS_DICT)
        account = Account(**ACCOUNT_DEV_DICT)
        job_id = "my-scheduled-job"

        await self.backend.get_job_by_id(job_id, user, account)
        self.backend.client.get_job_by_id.assert_awaited_with(
            f"{account.namespace}-{job_id}"
        )

    @with_json_fixture("scheduled-jobs/chronos/infra-purge-logs-job.json")
    async def test_get_job_by_id_job_exists(self, job_fixture):
        job_fixture["name"] = "dev-scheduled-job"
        async with http_client as client:
            await client.post(
                f"{settings.SCHEDULED_JOBS_SERVICE_ADDRESS}/v1/scheduler/iso8601",
                json=job_fixture,
            )

        user = User(**USER_WITH_MULTIPLE_ACCOUNTS_DICT)
        account = Account(**ACCOUNT_DEV_DICT)
        job_id = "scheduled-job"

        job = await self.backend.get_job_by_id(job_id, user, account)
        self.assertEqual(job_id, job.id)

    async def test_get_job_by_id_service_unavailable(self):
        """
        Por enquanto deixamos o erro ser propagado.
        """
        get_job_by_id_mock = CoroutineMock(
            side_effect=aiohttp.ClientConnectionError()
        )
        self.backend.client = CoroutineMock(spec=ChronosClient)
        self.backend.client.get_job_by_id = get_job_by_id_mock

        user = User(**USER_WITH_MULTIPLE_ACCOUNTS_DICT)
        account = Account(**ACCOUNT_DEV_DICT)

        with self.assertRaises(aiohttp.ClientConnectionError):
            await self.backend.get_job_by_id("job-id", user, account)
