from asynctest import TestCase, skip
from tests.utils import with_json_fixture

from asgard.backends.chronos.models.converters import (
    ChronosScheduledJobConverter,
)
from asgard.clients.chronos.models.job import ChronosJob
from asgard.models.job import ScheduledJob


class ChronosScheduledJobConverterTest(TestCase):
    async def setUp(self):
        self.maxDiff = None

    @with_json_fixture("scheduled-jobs/chronos/infra-purge-logs-job.json")
    async def test_convert_to_asgard_model_full_model(
        self, chronos_job_fixture
    ):
        """
        Validamos a transformação de todos os campos e sub-campos.
        """
        chronos_job = ChronosJob(**chronos_job_fixture)
        asgard_scheduled_job = ChronosScheduledJobConverter.to_asgard_model(
            chronos_job
        )
        asgard_scheduled_job_dict = asgard_scheduled_job.dict()
        self.assertEqual(
            {
                "id": chronos_job_fixture["name"],
                "description": chronos_job_fixture["description"],
                "enabled": True,
                "shell": True,
                "command": "sleep 10",
                "arguments": chronos_job_fixture["arguments"],
                "cpus": 0.1,
                "mem": 64,
                "disk": 0,
                "retries": 2,
                "concurrent": False,
                "container": {
                    "image": "alpine:3.4",
                    "ports": None,
                    "privileged": False,
                    "pull_image": False,
                    "type": "DOCKER",
                    "network": "BRIDGE",
                    "parameters": [
                        {"name": "a-docker-option", "value": "a-docker-value"},
                        {"name": "b-docker-option", "value": "yyy"},
                    ],
                    "volumes": [
                        {
                            "container_path": "/var/log/",
                            "host_path": "/logs/",
                            "mode": "RW",
                            "persistent": False,
                            "external": False,
                        }
                    ],
                },
                "env": {
                    "ENV_1": "VALUE_1",
                    "ENV_2": "VALUE_2",
                    "ENV_3": "VALUE_3",
                },
                "fetch": [
                    {
                        "uri": "file:///etc/docker.tar.bz2",
                        "executable": False,
                        "cache": False,
                        "extract": True,
                    },
                    {
                        "uri": "https://static.server.com/file.txt",
                        "executable": False,
                        "cache": False,
                        "extract": False,
                    },
                ],
                "constraints": [
                    "hostname:LIKE:10.0.0.1",
                    "workload:LIKE:general",
                ],
                "schedule": {
                    "value": "R/2019-07-12T12:00:00.000Z/PT24H",
                    "tz": "UTC",
                },
            },
            asgard_scheduled_job_dict,
        )

    @with_json_fixture("scheduled-jobs/chronos/infra-purge-logs-job.json")
    async def test_convert_to_asgard_model_enabled_field(
        self, chronos_job_fixture
    ):
        """
        O Campo orignal no chronos é "disabled". Como nosso campo é
        "enabled", os valores devem ser invertidos no momento da conversão
        dos modelos
        """
        chronos_job = ChronosJob(**chronos_job_fixture)
        asgard_scheduled_job = ChronosScheduledJobConverter.to_asgard_model(
            chronos_job
        )
        self.assertTrue(asgard_scheduled_job.enabled)

        chronos_job.disabled = True
        asgard_scheduled_job = ChronosScheduledJobConverter.to_asgard_model(
            chronos_job
        )
        self.assertFalse(asgard_scheduled_job.enabled)

    @with_json_fixture("scheduled-jobs/chronos/infra-purge-logs-job.json")
    async def test_convert_to_asgard_model_schedule_field(
        self, chronos_job_fixture
    ):
        chronos_job = ChronosJob(**chronos_job_fixture)
        asgard_job = ChronosScheduledJobConverter.to_asgard_model(chronos_job)
        self.assertEqual(
            {
                "value": chronos_job_fixture["schedule"],
                "tz": chronos_job_fixture["scheduleTimeZone"],
            },
            asgard_job.schedule.dict(),
        )

    @with_json_fixture("scheduled-jobs/chronos/infra-purge-logs-job.json")
    async def test_convert_to_asgard_model_container_field(
        self, chronos_job_fixture
    ):
        chronos_job = ChronosJob(**chronos_job_fixture)
        asgard_job = ChronosScheduledJobConverter.to_asgard_model(chronos_job)
        chronos_volumes_dict = chronos_job_fixture["container"]["volumes"]
        chronos_param_dict = chronos_job_fixture["container"]["parameters"]
        self.assertEqual(
            {
                "type": "DOCKER",
                "image": chronos_job_fixture["container"]["image"],
                "network": chronos_job_fixture["container"]["network"],
                "ports": None,
                "privileged": False,
                "parameters": [
                    {
                        "name": chronos_param_dict[0]["key"],
                        "value": chronos_param_dict[0]["value"],
                    },
                    {
                        "name": chronos_param_dict[1]["key"],
                        "value": chronos_param_dict[1]["value"],
                    },
                ],
                "pull_image": False,
                "volumes": [
                    {
                        "container_path": chronos_volumes_dict[0][
                            "containerPath"
                        ],
                        "host_path": chronos_volumes_dict[0]["hostPath"],
                        "mode": "RW",
                        "external": False,
                        "persistent": False,
                    }
                ],
            },
            asgard_job.container.dict(),
        )

    @with_json_fixture("scheduled-jobs/chronos/infra-purge-logs-job.json")
    async def test_convert_to_asgard_model_env_field(self, chronos_job_fixture):
        chronos_job = ChronosJob(**chronos_job_fixture)
        asgard_job = ChronosScheduledJobConverter.to_asgard_model(chronos_job)
        self.assertEqual(
            {"ENV_1": "VALUE_1", "ENV_2": "VALUE_2", "ENV_3": "VALUE_3"},
            asgard_job.dict()["env"],
        )

    @with_json_fixture("scheduled-jobs/chronos/infra-purge-logs-job.json")
    async def test_convert_to_asgard_model_fetch_field(
        self, chronos_job_fixture
    ):
        chronos_job = ChronosJob(**chronos_job_fixture)
        asgard_job = ChronosScheduledJobConverter.to_asgard_model(chronos_job)
        self.assertEqual(
            [
                {
                    "uri": "file:///etc/docker.tar.bz2",
                    "executable": False,
                    "cache": False,
                    "extract": True,
                },
                {
                    "uri": "https://static.server.com/file.txt",
                    "executable": False,
                    "cache": False,
                    "extract": False,
                },
            ],
            asgard_job.fetch,
        )

    @with_json_fixture("scheduled-jobs/chronos/infra-purge-logs-job.json")
    async def test_convert_to_asgard_model_constraints_field(
        self, chronos_job_fixture
    ):
        chronos_job = ChronosJob(**chronos_job_fixture)
        asgard_job = ChronosScheduledJobConverter.to_asgard_model(chronos_job)
        self.assertEqual(
            ["hostname:LIKE:10.0.0.1", "workload:LIKE:general"],
            asgard_job.constraints,
        )

    @skip("")
    async def test_to_client_model_env_field(self):

        asgard_dict_with_env_data = {
            "cpus": 1,
            "mem": 32,
            "description": "Example",
            "schedule": {"value": "2019"},
            "container": {"image": "alpine", "network": "BRIDGE"},
            "env": {
                "SERVICE_A_ADDRESS": "https://a.service.local",
                "SERVICE_B_ADDRESS": "https://b.service.local",
            },
        }
        asgard_scheduled_job = ScheduledJob(**asgard_dict_with_env_data)
        chronos_job = ChronosScheduledJobConverter.to_client_model(
            asgard_scheduled_job
        )
        self.assertEqual(
            [
                {
                    "key": "SERVICE_A_ADDRESS",
                    "value": "https://a.service.local",
                },
                {
                    "key": "SERVICE_B_ADDRESS",
                    "value": "https://b.service.local",
                },
            ],
            chronos_job.environmentVariables.dict(),
        )

    @skip("")
    async def test_convert_to_client_model(self):
        self.fail()

    @skip("")
    async def test_convert_to_client_include_sub_models(self):
        """
        Confirma que os campos que são, na verdade, sub-modelos também são
        incluídos na conversão.
        """
        self.fail()
