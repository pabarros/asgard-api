from asynctest import TestCase
from pydantic import ValidationError

from asgard.models.job import ScheduledJob


class ScheduledJobModelTest(TestCase):
    async def setUp(self):
        self.container_spec = {"image": "alpine:3", "network": "BRIDGE"}
        self.schedule_spec = {
            "value": "20190811T2100+00:00/R",
            "tz": "America/Sao_Paulo",
        }

        self.required_fields_scheduled_job = {
            "id": "my-sheduled-app",
            "cpus": 5.0,
            "mem": 512,
            "container": {**self.container_spec},
            "schedule": self.schedule_spec,
            "description": "A Scheduled Task",
        }

    async def test_serialized_parse_dict_required_fields(self):

        full_scheduled_job = {
            **self.required_fields_scheduled_job,
            "command": None,
            "arguments": None,
            "concurrent": False,
            "disk": 0,
            "container": {
                **self.container_spec,
                "parameters": None,
                "privileged": False,
                "pull_image": True,
                "volumes": None,
                "ports": None,
                "type": "DOCKER",
            },
            "schedule": {**self.schedule_spec},
            "env": None,
            "constraints": None,
            "fetch": None,
            "shell": False,
            "retries": 2,
            "enabled": True,
        }
        self.assertEqual(
            full_scheduled_job,
            ScheduledJob(**self.required_fields_scheduled_job).dict(),
        )

    async def test_valid_job_name(self):
        """
        O nome de cada job so poderá ter [a-z0-9-]
        """
        self.required_fields_scheduled_job["id"] = "a-valid-name-2"
        job = ScheduledJob(**self.required_fields_scheduled_job)
        self.assertEqual(self.required_fields_scheduled_job["id"], job.id)

    async def test_invalid_job_name(self):
        with self.assertRaises(ValidationError):
            self.required_fields_scheduled_job["id"] = "InvalidJobName"
            ScheduledJob(**self.required_fields_scheduled_job)
