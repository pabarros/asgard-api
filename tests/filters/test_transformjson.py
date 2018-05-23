import unittest

from hollowman.filters.transformjson import TransformJSONFilter
from hollowman.marathonapp import AsgardApp
from tests.utils import with_json_fixture


class TransformJSONTest(unittest.TestCase):

    def setUp(self):
        self.filter = TransformJSONFilter()

    @with_json_fixture("../fixtures/filters/app-json-new-format.json")
    def test_is_json_new_format_has_only_networks(self, app_json_new_format):
        """
        Confirma que conseguimos reconhecer um JSON já no formato novo
        Formato novo contém as chaves:
            * `networks`
            * `container.portMappings`
        """
        del app_json_new_format['container']['portMappings']
        asgard_app = AsgardApp.from_json(app_json_new_format)
        self.assertTrue(self.filter._is_new_format(asgard_app))

    @with_json_fixture("../fixtures/filters/app-json-new-format.json")
    def test_is_json_new_format_has_only_port_mappings(self, app_json_new_format):
        del app_json_new_format['networks']
        asgard_app = AsgardApp.from_json(app_json_new_format)
        self.assertTrue(self.filter._is_new_format(asgard_app))

    @with_json_fixture("../fixtures/single_full_app.json")
    def test_is_not_json_new_format(self, single_full_app_fixture):
        asgard_app = AsgardApp.from_json(single_full_app_fixture)
        self.assertFalse(self.filter._is_new_format(asgard_app))

    def test_transform_json_network_already_new_format_before_upstream_request(self):
        """
        Não fazemos nada se o JSON já estiver no formato novo, ou seja, com a chave `networks` (na raiz).
        """
        self.fail()

    def test_transform_json_change_network_before_upstream_request(self):
        """
        Movemos o dict de `container.docker.network` para `netowks`
        """
        self.fail()

    def test_transform_json_change_port_mappings_already_new_format_before_upstream_request(self):
        """
        Não fazemos nada se o JSON já possui a key `container.portMappings`
        """
        self.fail()

    def test_transform_json_change_port_mappings_before_upstream_request(self):
        """
        Movemos `container.docker.portMappings` para `container.portMappings`
        """
        self.fail()

    def test_transform_json_change_network_already_new_format_before_response_to_client(self):
        self.fail()

    def test_transform_json_change_network_before_response_to_client(self):
        self.fail()

    def test_transform_json_change_port_mappings_already_new_format_before_response_to_client(self):
        self.fail()

    def test_transform_json_change_port_mappings_before_response_to_client(self):
        self.fail()

