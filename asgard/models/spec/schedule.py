from asgard.models.base import BaseModel


class ScheduleSpec(BaseModel):
    type = "ASGARD"
    value: str
    tz: str = "UTC"
