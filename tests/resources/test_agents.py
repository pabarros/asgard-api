import unittest

from pydantic import ValidationError

from asgard.api.resources.agents import AgentsResource
from asgard.backends.mesos import MesosAgent


class AgentsTests(unittest.TestCase):
    def test_it_instantiates_a_agentsresource_if_type_is_valid(self):
        agents = [
            dict(
                type="MESOS",
                id="id",
                hostname="hostname",
                active="active",
                version="version",
                port=8080,
                used_resources={"bla": "used_resources"},
                attributes={"data": "attributes"},
                resources={"data": "resources"},
            )
        ]
        resource = AgentsResource(agents=agents)

        self.assertIsInstance(resource, AgentsResource)
        for agent in resource.agents:
            self.assertIsInstance(agent, MesosAgent)

    def test_it_raises_a_validation_error_if_type_is_invalid(self):
        agents = [
            dict(
                type="XABLAU",
                id="id",
                hostname="hostname",
                active="active",
                version="version",
                port=8080,
                used_resources={"bla": "used_resources"},
                attributes={"data": "attributes"},
                resources={"data": "resources"},
            )
        ]
        with self.assertRaises(ValidationError):
            AgentsResource(agents=agents)