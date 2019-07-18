from typing import Optional

import aiohttp

from asgard.backends.chronos.models.converters import (
    ChronosScheduledJobConverter,
)
from asgard.backends.jobs import ScheduledJobsBackend
from asgard.clients.chronos import ChronosClient, Http404
from asgard.conf import settings
from asgard.models.account import Account
from asgard.models.job import ScheduledJob
from asgard.models.user import User


class ChronosScheduledJobsBackend(ScheduledJobsBackend):
    def __init__(self) -> None:
        self.client = ChronosClient(settings.SCHEDULED_JOBS_SERVICE_ADDRESS)

    async def get_job_by_id(
        self, job_id: str, user: User, account: Account
    ) -> Optional[ScheduledJob]:
        namespaced_job_id = f"{account.namespace}-{job_id}"
        try:
            chronos_job = await self.client.get_job_by_id(namespaced_job_id)
            if chronos_job:
                scheduled_job = ChronosScheduledJobConverter.to_asgard_model(
                    chronos_job
                )
                return scheduled_job
        except Http404:
            return None
        return None

    async def update_job(
        self, job: ScheduledJobsBackend
    ) -> ScheduledJobsBackend:
        pass
