import unittest
from hollowman.filters.labels import LabelsFilter
from hollowman.marathonapp import AsgardApp

from tests.utils import with_json_fixture


class RemoveLabelsFilterTest(unittest.TestCase):
    @with_json_fixture("../fixtures/single_full_app.json")
    def setUp(self, single_full_app_fixture):
        self.filter = LabelsFilter()
        self.single_full_app_fixture = single_full_app_fixture
        self.request_app = AsgardApp.from_json(self.single_full_app_fixture)
        self.original_app = AsgardApp.from_json(self.single_full_app_fixture)

    def test_create_app_remove_traefik_backend_label_do_not_exist(self):
        filtered_app = self.filter.write(None, self.request_app, AsgardApp())
        self.assertFalse("traefik.backend" in filtered_app.labels.keys())

    def test_create_app_remove_traefik_backend_label_exists(self):
        self.request_app.labels["traefik.backend"] = "my-app-backend"
        filtered_app = self.filter.write(None, self.request_app, AsgardApp())
        self.assertFalse("traefik.backend" in filtered_app.labels.keys())

    def test_update_app_remove_traefik_backend_label_exists(self):
        self.request_app.labels["traefik.backend"] = "my-app-backend"
        filtered_app = self.filter.write(None, self.request_app, AsgardApp())
        self.assertFalse("traefik.backend" in filtered_app.labels.keys())

    def test_update_app_remove_traefik_backend_label_do_not_exist(self):
        filtered_app = self.filter.write(None, self.request_app, AsgardApp())
        self.assertFalse("traefik.backend" in filtered_app.labels.keys())
