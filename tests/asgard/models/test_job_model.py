from asynctest import TestCase

from asgard.models.job import ScheduledJob


class ScheduledJobModelTest(TestCase):
    async def test_serialized_parse_dict_required_fields(self):
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

        full_scheduled_job = {
            **required_fields_scheduled_job,
            "command": None,
            "arguments": None,
            "concurrent": False,
            "disk": 0,
            "container": {
                **container_spec,
                "parameters": None,
                "privileged": False,
                "pull_image": True,
                "volumes": None,
                "ports": None,
                "type": "ASGARD",
            },
            "schedule": {**schedule_spec, "type": "ASGARD"},
            "env": None,
            "constraints": None,
            "fetch": None,
            "shell": False,
            "retries": 2,
            "enabled": True,
            "type": "ASGARD",
        }
        self.assertEqual(
            full_scheduled_job,
            ScheduledJob(**required_fields_scheduled_job).dict(),
        )
