

import unittest

from hollowman.filters.incompatiblefields import IncompatibleFieldsFilter
from hollowman.marathonapp import SieveMarathonApp
from hollowman.dispatcher import merge_marathon_apps

from tests.utils import with_json_fixture


class IncompatibleFieldsFilterTest(unittest.TestCase):

    @with_json_fixture("../fixtures/single_full_app.json")
    def setUp(self, single_full_app_fixture):
        self.single_full_app_fixture = single_full_app_fixture
        self.filter = IncompatibleFieldsFilter()
        self.request_app = SieveMarathonApp.from_json(self.single_full_app_fixture)
        self.original_app = SieveMarathonApp.from_json(self.single_full_app_fixture)

    def test_update_app_remove_ports_fields(self):
        self.original_app.ports = self.single_full_app_fixture['container']['docker']['portMappings'][0]['servicePort']
        merged_app = merge_marathon_apps(self.original_app, self.request_app)
        filtered_app = self.filter.write(None, merged_app, self.original_app)
        self.assertEqual([], filtered_app.ports)

