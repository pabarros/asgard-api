import os
import unittest
from unittest import mock

from hollowman.app import application
from hollowman.filters.transformjson import TransformJSONFilter
from hollowman.marathonapp import AsgardApp
from tests.utils import with_json_fixture


class TransformJSONTest(unittest.TestCase):
    def setUp(self):
        self.filter = TransformJSONFilter()
        self.env_patcher = mock.patch.dict(
            os.environ, ASGARD_FILTER_TRANSFORMJSON_ENABLED="1"
        )
        self.env_patcher.start()
        self.flask_req_ctx = application.test_request_context(
            "/v2/apps/dev/foo", headers={"X-UI-Version": "new"}
        )
        self.flask_req_ctx.push()

    def tearDown(self):
        self.env_patcher.stop()
        self.flask_req_ctx.pop()

    @with_json_fixture("../fixtures/filters/app-json-new-format.json")
    def test_is_json_new_format_has_only_networks(self, app_json_new_format):
        """
        Confirma que conseguimos reconhecer um JSON já no formato novo
        Formato novo contém as chaves:
            * `networks`
            * `container.portMappings`
        """
        del app_json_new_format["container"]["portMappings"]
        asgard_app = AsgardApp.from_json(app_json_new_format)
        self.assertTrue(self.filter._is_new_format(asgard_app))

    @with_json_fixture("../fixtures/filters/app-json-new-format.json")
    def test_transform_to_new_does_not_have_old_network(
        self, app_json_new_format
    ):
        asgard_app = AsgardApp.from_json(app_json_new_format)
        filtered_app = self.filter._transform_to_new_format(asgard_app)
        self.assertEqual(
            app_json_new_format["container"]["portMappings"][0],
            filtered_app.container.port_mappings[0].json_repr(),
        )

        self.assertTrue(hasattr(filtered_app.container, "port_mappings"))
        self.assertTrue(hasattr(filtered_app, "networks"))
        self.assertEqual("container/bridge", filtered_app.networks[0]["mode"])

    @with_json_fixture("../fixtures/filters/app-json-new-format.json")
    def test_is_json_new_format_has_only_port_mappings(
        self, app_json_new_format
    ):
        del app_json_new_format["networks"]
        asgard_app = AsgardApp.from_json(app_json_new_format)
        self.assertTrue(self.filter._is_new_format(asgard_app))

    @with_json_fixture("../fixtures/single_full_app.json")
    def test_is_not_json_new_format(self, single_full_app_fixture):
        asgard_app = AsgardApp.from_json(single_full_app_fixture)
        self.assertFalse(self.filter._is_new_format(asgard_app))

    @with_json_fixture("../fixtures/filters/app-json-new-format.json")
    def test_transform_json_before_upstream_request_network_bridge(
        self, app_json_new_format
    ):
        """
        JSON novo > JSON velho antes de mandar pro backend
        """
        request_app = AsgardApp.from_json(app_json_new_format)
        original_app = AsgardApp.from_json(app_json_new_format)
        filtered_app = self.filter.write(None, request_app, original_app)

        self.assertEqual(filtered_app.container.docker.network, "BRIDGE")
        self.assertTrue(filtered_app.container.docker.port_mappings)
        self.assertEqual(
            app_json_new_format["container"]["portMappings"][0],
            filtered_app.container.docker.port_mappings[0].json_repr(),
        )

        self.assertFalse(hasattr(filtered_app.container, "port_mappings"))
        self.assertFalse(hasattr(filtered_app, "networks"))

    @with_json_fixture("../fixtures/filters/app-json-new-format.json")
    def test_transform_json_before_upstream_request_network_host(
        self, app_json_new_format
    ):
        """
        JSON novo > JSON velho antes de mandar pro backend
        """
        app_json_new_format["networks"][0]["mode"] = "host"
        request_app = AsgardApp.from_json(app_json_new_format)
        original_app = AsgardApp.from_json(app_json_new_format)
        filtered_app = self.filter.write(None, request_app, original_app)

        self.assertEqual(filtered_app.container.docker.network, "HOST")
        self.assertTrue(filtered_app.container.docker.port_mappings)
        self.assertEqual(
            app_json_new_format["container"]["portMappings"][0],
            filtered_app.container.docker.port_mappings[0].json_repr(),
        )

        self.assertFalse(hasattr(filtered_app.container, "port_mappings"))
        self.assertFalse(hasattr(filtered_app, "networks"))

    @with_json_fixture("../fixtures/filters/app-json-new-format.json")
    def test_transform_json_before_upstream_absent_port_mappings(
        self, app_json_new_format
    ):
        del app_json_new_format["container"]["portMappings"]
        request_app = AsgardApp.from_json(app_json_new_format)
        original_app = AsgardApp.from_json(app_json_new_format)
        filtered_app = self.filter.write(None, request_app, original_app)

        self.assertIsNone(filtered_app.container.docker.port_mappings)

        self.assertFalse(hasattr(filtered_app.container, "port_mappings"))
        self.assertFalse(hasattr(filtered_app, "networks"))

    @with_json_fixture("../fixtures/single_full_app.json")
    def test_transform_json_to_new_format_change_network_before_response_to_client(
        self, full_app_old_format
    ):
        """
        Movemos o dict de `container.docker.network` para `networks`
        """
        del full_app_old_format["container"]["docker"]["portMappings"]
        request_app = AsgardApp.from_json(full_app_old_format)
        original_app = AsgardApp.from_json(full_app_old_format)

        filtered_app = self.filter.response(None, request_app, original_app)
        self.assertTrue(filtered_app.networks)
        self.assertEqual(1, len(filtered_app.networks))
        self.assertEqual("container/bridge", filtered_app.networks[0]["mode"])

    @with_json_fixture("../fixtures/single_full_app.json")
    def test_transform_json_to_new_format_network_host_before_response_to_client(
        self, full_app_old_format
    ):
        """
        Movemos o dict de `container.docker.network` para `networks`
        """
        del full_app_old_format["container"]["docker"]["portMappings"]
        full_app_old_format["container"]["docker"]["network"] = "HOST"
        request_app = AsgardApp.from_json(full_app_old_format)
        original_app = AsgardApp.from_json(full_app_old_format)

        filtered_app = self.filter.response(None, request_app, original_app)
        self.assertTrue(filtered_app.networks)
        self.assertEqual(1, len(filtered_app.networks))
        self.assertEqual("host", filtered_app.networks[0]["mode"])

    @with_json_fixture("../fixtures/filters/app-json-new-format.json")
    def test_transform_json_already_new_format_before_response_to_client(
        self, app_json_new_format
    ):
        """
        Não fazemos nada se o JSOM que vem do backend ja estiver no formato novo.
        Isso vai acontecr quando atualizarmos pro Marathon 1.5.t
        """
        response_app = AsgardApp.from_json(app_json_new_format)
        original_app = AsgardApp.from_json(app_json_new_format)

        filtered_app = self.filter.response(None, response_app, original_app)

        self.assertTrue(filtered_app.networks)
        self.assertTrue(hasattr(filtered_app.container, "port_mappings"))
        # O model da App tem o campo, mas deve estar vazio
        self.assertFalse(filtered_app.container.docker.port_mappings)
        self.assertFalse(hasattr(filtered_app.container.docker, "network"))

    @with_json_fixture("../fixtures/single_full_app.json")
    def test_transform_json_to_new_format_change_port_mappings_before_response_to_client(
        self, full_app_old_format
    ):
        """
        Movemos `container.docker.portMappings` para `container.portMappings`
        Especificamente nesse teste a App possui `container.portMappings`
        """
        request_app = AsgardApp.from_json(full_app_old_format)
        original_app = AsgardApp.from_json(full_app_old_format)

        self.assertFalse(hasattr(request_app.container, "port_mappings"))
        filtered_app = self.filter.response(None, request_app, original_app)

        self.assertTrue(filtered_app.container.port_mappings)
        expected_port_mappings = full_app_old_format["container"]["docker"][
            "portMappings"
        ]
        self.assertEqual(
            len(expected_port_mappings),
            len(filtered_app.container.port_mappings),
        )
        self.assertEqual(
            expected_port_mappings[0],
            filtered_app.container.port_mappings[0].json_repr(),
        )

    @with_json_fixture("../fixtures/filters/app-json-new-format.json")
    @with_json_fixture("../fixtures/single_full_app.json")
    def test_noop_if_env_is_disabled(
        self, app_json_new_format, app_json_old_format
    ):
        """
        O filtro nao deve rodar se a não houver indicações de que a UI já é a versão nova.
        Essa indicação é feita através de um header `X-UI-Version` que é passado em todos os requests (apenas pela UI nova)
        """
        with mock.patch.dict(
            os.environ, ASGARD_FILTER_TRANSFORMJSON_ENABLED="0"
        ), application.test_request_context("/v2/apps/dev/foo", headers={}):
            asgard_app_new_format = AsgardApp.from_json(app_json_new_format)
            asgard_app_old_format = AsgardApp.from_json(app_json_old_format)

            filterd_before_upstream_request = self.filter.write(
                None, asgard_app_new_format, asgard_app_new_format
            )
            filterd_before_response_to_client = self.filter.response(
                None, asgard_app_old_format, asgard_app_old_format
            )

            # Não convertemos a App para formato velho
            self.assertEqual(
                filterd_before_upstream_request.networks,
                app_json_new_format["networks"],
            )
            self.assertEqual(
                filterd_before_upstream_request.container.port_mappings[
                    0
                ].json_repr(),
                app_json_new_format["container"]["portMappings"][0],
            )
            self.assertFalse(
                hasattr(
                    filterd_before_upstream_request.container.docker, "network"
                )
            )
            self.assertFalse(
                filterd_before_upstream_request.container.docker.port_mappings
            )

            # Não convertemos a app para o formato novo
            self.assertFalse(filterd_before_response_to_client.networks)
            self.assertFalse(
                hasattr(
                    filterd_before_response_to_client.container, "port_mappings"
                )
            )
            self.assertEqual(
                filterd_before_response_to_client.container.docker.network,
                app_json_old_format["container"]["docker"]["network"],
            )
            self.assertEqual(
                filterd_before_response_to_client.container.docker.port_mappings[
                    0
                ].json_repr(),
                app_json_old_format["container"]["docker"]["portMappings"][0],
            )
