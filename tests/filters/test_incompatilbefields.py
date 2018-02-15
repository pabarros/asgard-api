

import unittest

from hollowman.filters.incompatiblefields import IncompatibleFieldsFilter
from hollowman.marathonapp import AsgardApp
from hollowman.http_wrappers.request import Request

from tests.utils import with_json_fixture


class IncompatibleFieldsFilterTest(unittest.TestCase):

    @with_json_fixture("../fixtures/single_full_app.json")
    def setUp(self, single_full_app_fixture):
        self.request = Request(None)
        self.single_full_app_fixture = single_full_app_fixture
        self.filter = IncompatibleFieldsFilter()
        self.request_app = AsgardApp.from_json(self.single_full_app_fixture)
        self.original_app = AsgardApp.from_json(self.single_full_app_fixture)

    def test_update_app_remove_ports_fields(self):
        self.original_app.ports = self.single_full_app_fixture['container']['docker']['portMappings'][0]['servicePort']
        merged_app = self.request.merge_marathon_apps(self.original_app, self.request_app)
        filtered_app = self.filter.write(None, merged_app, self.original_app)
        self.assertEqual([], filtered_app.ports)

    def test_update_app_remove_port_definitions_fields(self):
        port_definitions = [
            {
                "port": 10019,
                "protocol": "tcp",
                "name": "http",
                "labels": {
                    "vip": "192.168.0.1:80"
                }
            }
        ]
        self.original_app.port_definitions = port_definitions
        merged_app = self.request.merge_marathon_apps(self.original_app, self.request_app)
        filtered_app = self.filter.write(None, merged_app, self.original_app)
        self.assertEqual([], filtered_app.port_definitions)
