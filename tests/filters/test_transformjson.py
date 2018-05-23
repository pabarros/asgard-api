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

    def test_transform_json_network_already_new_format_before_upstream_request(self, app_json_new_format):
        """
        Não fazemos nada se o JSON a App já estiver no formato novo.
        Especificamente nesse teste a App possui o `networks` mas não possui o `container.portMappings`
        """
        self.fail()

    def test_transform_json_change_network_before_upstream_request(self, full_app_old_format):
        self.fail()

    def test_transform_json_change_port_mappings_already_new_format_before_upstream_request(self):
        """
        Não fazemos nada se o JSON a App já estiver no formato novo.
        """
        self.fail()

    def test_transform_json_change_port_mappings_before_upstream_request(self, full_app_old_format):
        self.fail()

    def test_transform_json_change_network_already_new_format_before_response_to_client(self):
        self.fail()

    @with_json_fixture("../fixtures/single_full_app.json")
    def test_transform_json_to_new_format_change_network_before_response_to_client(self, full_app_old_format):
        """
        Movemos o dict de `container.docker.network` para `netowks`
        """
        del full_app_old_format['container']['docker']['portMappings']
        request_app = AsgardApp.from_json(full_app_old_format)
        original_app = AsgardApp.from_json(full_app_old_format)

        filtered_app = self.filter.write(None, request_app, original_app)
        self.assertTrue(filtered_app.networks)
        self.assertEqual(1, len(filtered_app.networks))
        self.assertEqual("container/bridge", filtered_app.networks[0]['name'])

    def test_transform_json_change_port_mappings_already_new_format_before_response_to_client(self):
        self.fail()

    @with_json_fixture("../fixtures/single_full_app.json")
    def test_transform_json_to_new_format_change_port_mappings_before_response_to_client(self, full_app_old_format):
        """
        Movemos `container.docker.portMappings` para `container.portMappings`
        Especificamente nesse teste a App possui `container.portMappings`
        """
        request_app = AsgardApp.from_json(full_app_old_format)
        original_app = AsgardApp.from_json(full_app_old_format)

        self.assertFalse(hasattr(request_app.container, "port_mappings"))
        filtered_app = self.filter.response(None, request_app, original_app)

        self.assertTrue(filtered_app.container.port_mappings)
        expected_port_mappings = full_app_old_format['container']['docker']['portMappings']
        self.assertEqual(len(expected_port_mappings), len(filtered_app.container.port_mappings))
        self.assertEqual(expected_port_mappings[0], filtered_app.container.port_mappings[0].json_repr())

