import unittest

from pydantic import ValidationError

from asgard.api.resources.apps import AppsResource
from asgard.backends.mesos import MesosApp


class AppsResourceTests(unittest.TestCase):
    def test_it_instantiates_a_agentsresource_if_type_is_valid(self):
        apps = [
            dict(
                type="MESOS",
                id="sieve_infra_asgard_async-api.7e5d20eb-248a-11e9-91ea-024286d5b96a",
                source="sieve_infra_asgard_async-api.7e5d20eb-248a-11e9-91ea-024286d5b96a",
                framework_id="27b52920-3899-4b90-a1d6-bf83a87f3612-0000",
            )
        ]
        resource = AppsResource(apps=apps)

        self.assertIsInstance(resource, AppsResource)
        for agent in resource.apps:
            self.assertIsInstance(agent, MesosApp)

    def test_it_instantiates_a_agentsresource_using_agents_instances(self):
        apps = [
            MesosApp(
                **dict(
                    id="sieve_infra_asgard_async-api.7e5d20eb-248a-11e9-91ea-024286d5b96a",
                    source="sieve_infra_asgard_async-api.7e5d20eb-248a-11e9-91ea-024286d5b96a",
                    framework_id="27b52920-3899-4b90-a1d6-bf83a87f3612-0000",
                )
            )
        ]
        resource = AppsResource(apps=apps)

        self.assertIsInstance(resource, AppsResource)
        for agent in resource.apps:
            self.assertIsInstance(agent, MesosApp)

    def test_it_raises_a_validation_error_if_type_is_invalid(self):
        apps = [
            dict(
                type="XABLAU",
                id="sieve_infra_asgard_async-api.7e5d20eb-248a-11e9-91ea-024286d5b96a",
                source="sieve_infra_asgard_async-api.7e5d20eb-248a-11e9-91ea-024286d5b96a",
                framework_id="27b52920-3899-4b90-a1d6-bf83a87f3612-0000",
            )
        ]
        with self.assertRaises(ValidationError):
            AppsResource(apps=apps)
