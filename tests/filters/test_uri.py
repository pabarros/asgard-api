
from copy import copy
import unittest

from hollowman.filters.uri import AddURIFilter
from hollowman.marathonapp import SieveMarathonApp

from tests.utils import with_json_fixture

class AddURIFilterTest(unittest.TestCase):

    @with_json_fixture("../fixtures/single_full_app.json")
    def setUp(self, single_full_app_fixture):
        self.docker_auth_uri = "file:///etc/docker.tar.bz2"
        self.base_uris = ["http://google.com", "file://etc/file.txt"]
        self.single_full_app_fixture = single_full_app_fixture
        self.request_app = SieveMarathonApp.from_json(self.single_full_app_fixture)
        self.original_app = SieveMarathonApp.from_json(self.single_full_app_fixture)
        self.filter = AddURIFilter()

    def test_update_app_do_not_add_uri_if_exist(self):
        self.single_full_app_fixture['uris'] = copy(self.base_uris) + [self.docker_auth_uri]
        self.request_app = SieveMarathonApp.from_json(self.single_full_app_fixture)
        filtered_app = self.filter.write(None, self.request_app, self.original_app)
        self.assertEqual(3, len(filtered_app.uris))
        self.assertEqual(self.base_uris + [self.docker_auth_uri], filtered_app.uris)

    def test_update_app_add_uri_with_other_existing_uris(self):
        """
        Mesmo se a app já tiver utras uris, temos que adicionar a nossa
        """
        self.single_full_app_fixture['uris'] = copy(self.base_uris)
        self.request_app = SieveMarathonApp.from_json(self.single_full_app_fixture)
        filtered_app = self.filter.write(None, self.request_app, self.original_app)
        self.assertEqual(3, len(filtered_app.uris))
        self.assertEqual(self.base_uris + [self.docker_auth_uri], filtered_app.uris)

    def test_update_app_add_uri_if_not_exist(self):
        self.request_app = SieveMarathonApp.from_json(self.single_full_app_fixture)
        filtered_app = self.filter.write(None, self.request_app, self.original_app)
        self.assertEqual(1, len(filtered_app.uris))
        self.assertEqual([self.docker_auth_uri], filtered_app.uris)

    def test_create_app_add_uri_if_not_exist(self):
        self.request_app = SieveMarathonApp.from_json(self.single_full_app_fixture)
        filtered_app = self.filter.write(None, self.request_app, SieveMarathonApp())
        self.assertEqual(1, len(filtered_app.uris))
        self.assertEqual([self.docker_auth_uri], filtered_app.uris)

    def test_create_app_do_not_add_uri_if_exist(self):
        self.single_full_app_fixture['uris'] = copy(self.base_uris) + [self.docker_auth_uri]
        self.request_app = SieveMarathonApp.from_json(self.single_full_app_fixture)
        filtered_app = self.filter.write(None, self.request_app, SieveMarathonApp())
        self.assertEqual(3, len(filtered_app.uris))
        self.assertEqual(self.base_uris + [self.docker_auth_uri], filtered_app.uris)

    def test_create_app_add_uri_with_other_existing_uris(self):
        """
        Mesmo se a app já tiver utras uris, temos que adicionar a nossa
        """
        self.single_full_app_fixture['uris'] = copy(self.base_uris)
        self.request_app = SieveMarathonApp.from_json(self.single_full_app_fixture)
        filtered_app = self.filter.write(None, self.request_app, SieveMarathonApp())
        self.assertEqual(3, len(filtered_app.uris))
        self.assertEqual(self.base_uris + [self.docker_auth_uri], filtered_app.uris)
