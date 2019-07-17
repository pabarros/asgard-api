from asynctest import TestCase
from tests.utils import with_json_fixture

from asgard.backends.chronos.models.converters import (
    ChronosContainerSpecConverter,
)
from asgard.clients.chronos.models.job import ChronosContainerSpec
from asgard.models.spec.container import ContainerSpec


class ChronosContainerSpecConverterTest(TestCase):
    async def setUp(self):
        self.expected_asgard_container_dict = {
            "type": "DOCKER",
            "pull_image": False,
            "ports": None,
            "privileged": False,
            "image": "alpine:3.4",
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
                    "external": False,
                    "persistent": False,
                }
            ],
        }

    @with_json_fixture("scheduled-jobs/chronos/infra-purge-logs-job.json")
    async def test_to_asgard_model(self, chronos_job_fixture):
        self.maxDiff = None
        chronos_container_dict = chronos_job_fixture["container"]
        chronos_container_spec = ChronosContainerSpec(**chronos_container_dict)
        asgard_container_spec = ChronosContainerSpecConverter.to_asgard_model(
            chronos_container_spec
        )
        self.assertEqual(
            self.expected_asgard_container_dict, asgard_container_spec.dict()
        )

    async def test_to_client_model(self):
        asgard_container_spec = ContainerSpec(
            **self.expected_asgard_container_dict
        )
        chronos_container_spec = ChronosContainerSpecConverter.to_client_model(
            asgard_container_spec
        )
        self.assertEqual(
            {
                "forcePullImage": False,
                "image": "alpine:3.4",
                "network": "BRIDGE",
                "parameters": [
                    {"key": "a-docker-option", "value": "a-docker-value"},
                    {"key": "b-docker-option", "value": "yyy"},
                ],
                "type": "CHRONOS",
                "volumes": [
                    {
                        "containerPath": "/var/log/",
                        "hostPath": "/logs/",
                        "mode": "RW",
                    }
                ],
            },
            chronos_container_spec.dict(),
        )
