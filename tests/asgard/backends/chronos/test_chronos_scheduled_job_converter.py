from asynctest import TestCase
from tests.utils import with_json_fixture

from asgard.backends.chronos.models.converters import (
    ChronosScheduledJobConverter,
)
from asgard.clients.chronos.models.job import ChronosJob


class ChronosScheduledJobConverterTest(TestCase):
    async def setUp(self):
        self.maxDiff = None

    @with_json_fixture("scheduled-jobs/chronos/infra-purge-logs-job.json")
    async def test_convert_to_asgard_model_root_fields(
        self, chronos_job_fixture
    ):
        """
        Validamos a transformação de campos simples (não compostos) e que estão
        na raiz do objeto
        """
        chronos_job = ChronosJob(**chronos_job_fixture)
        asgard_scheduled_job = ChronosScheduledJobConverter.to_asgard_model(
            chronos_job
        )
        asgard_scheduled_job_dict = asgard_scheduled_job.dict()
        del asgard_scheduled_job_dict["container"]
        del asgard_scheduled_job_dict["schedule"]
        self.assertEqual(
            {
                "type": "CHRONOS",
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
                "env": None,
                "fetch": None,
                "constraints": None,
            },
            asgard_scheduled_job_dict,
        )

    async def test_convert_to_asgard_models_full_model(self):
        """
        Confere que um modelo completo (todos os campos e sub-campos) são
        convertidos corretamente.
        """
        self.fail()

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
                "type": "ASGARD",
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
                        "type": "ASGARD",
                        "name": chronos_param_dict[0]["key"],
                        "value": chronos_param_dict[0]["value"],
                    },
                    {
                        "type": "ASGARD",
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
                        "type": "ASGARD",
                    }
                ],
            },
            asgard_job.container.dict(),
        )

    @with_json_fixture("scheduled-jobs/chronos/infra-purge-logs-job.json")
    async def test_convert_to_asgard_model_env_field(self, chronos_job_fixture):
        self.fail()

    @with_json_fixture("scheduled-jobs/chronos/infra-purge-logs-job.json")
    async def test_convert_to_asgard_model_fetch_field(
        self, chronos_job_fixture
    ):
        self.fail()

    @with_json_fixture("scheduled-jobs/chronos/infra-purge-logs-job.json")
    async def test_convert_to_asgard_model_constraints_field(
        self, chronos_job_fixture
    ):
        self.fail()

    async def test_convert_to_client_model(self):
        self.fail()

    async def test_convert_to_client_include_sub_models(self):
        """
        Confirma que os campos que são, na verdade, sub-modelos também são
        incluídos na conversão.
        """
        self.fail()
