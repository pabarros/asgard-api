from typing import Optional

from asgard.backends.jobs import ScheduledJobsBackend
from asgard.models.account import Account
from asgard.models.job import ScheduledJob
from asgard.models.user import User


class ScheduledJobsService:
    @staticmethod
    async def get_job_by_id(
        job_id: str, user: User, account: Account, backend: ScheduledJobsBackend
    ) -> Optional[ScheduledJob]:
        return await backend.get_job_by_id(job_id, user, account)
