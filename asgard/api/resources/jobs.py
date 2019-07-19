from typing import Optional

from pydantic import BaseModel

from asgard.models.job import ScheduledJob


class ScheduledJobResource(BaseModel):
    job: Optional[ScheduledJob]
