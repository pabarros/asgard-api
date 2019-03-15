import logging
import os
import unittest
from unittest import mock

from hollowman import conf, plugins
from hollowman.app import application


class PluginLoaderTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_plugin_load_metrics_plugins(self):
        """
        Plugins do tipo Metric Plugin devem fornecer um objeto do tipo flask.Blueprint.
        Plugins que falharem em fornecer esse objeto não serão carregados

        Aqui temos um plugin, instalado via requirements-dev.txt chamado `asgard-api-plugin-metrics-example-1`
        esse plugin fornece 4 entrypoints. Apenas um dos entrypoints está 100% correto.

        O que esse teste confere é que quando carregamos esse plugin, apenas um novo endpoint é adicionado à
        app flask principal
        """
        logger_mock = mock.MagicMock()
        with mock.patch.multiple(conf, LOGLEVEL="DEBUG"):
            plugins.load_all_metrics_plugins(
                application,
                get_plugin_logger_instance=lambda plugin_id: logger_mock,
            )
        with application.test_client() as client:
            response = client.get(
                "/_cat/metrics/asgard-api-plugin-metrics-example-1/ping"
            )
            self.assertEqual(200, response.status_code)
            self.assertEqual(b"Metrics Plugin Example 1 OK", response.data)
            logger_mock.info.assert_called_with("Log from Mertrics Plugin")
            logger_mock.setLevel.assert_called_with(logging.DEBUG)

    def test_plugin_load_plugins_populate_internal_registry(self):
        """
        Certifica que populamos o registro interno contento o status de load de cada
        plugin
        """
        logger_mock = mock.MagicMock()
        with mock.patch.multiple(conf, LOGLEVEL="DEBUG"):
            plugins.PLUGINS_LOAD_STATUS["plugins"] = {}
            plugins.load_all_metrics_plugins(
                application,
                get_plugin_logger_instance=lambda plugin_id: logger_mock,
            )
            self.assertEqual(
                4,
                len(
                    plugins.PLUGINS_LOAD_STATUS["plugins"][
                        "asgard-api-plugin-metrics-example-1"
                    ]
                ),
            )
            plugin_status_data = plugins.PLUGINS_LOAD_STATUS["plugins"][
                "asgard-api-plugin-metrics-example-1"
            ]
            data_sorted = sorted(
                plugin_status_data,
                key=lambda item: item["entrypoint"]["function_name"],
            )
            self.assertEqual(4, len(data_sorted))

            expected_load_data = [
                {
                    "status": "FAIL",
                    "exception": "ImportError",
                    "traceback": mock.ANY,
                    "plugin_id": "asgard-api-plugin-metrics-example-1",
                    "entrypoint": {
                        "module_name": "metricpluginexample",
                        "function_name": "does_not_exist",
                    },
                }
            ]
            self.assertEqual(expected_load_data[0], data_sorted[0])

            expected_load_data = [
                {
                    "status": "FAIL",
                    "exception": "ZeroDivisionError",
                    "traceback": mock.ANY,
                    "plugin_id": "asgard-api-plugin-metrics-example-1",
                    "entrypoint": {
                        "module_name": "metricpluginexample",
                        "function_name": "plugin_init_exception",
                    },
                }
            ]
            self.assertEqual(expected_load_data[0], data_sorted[1])

            expected_load_data = [
                {
                    "status": "OK",
                    "plugin_id": "asgard-api-plugin-metrics-example-1",
                    "entrypoint": {
                        "module_name": "metricpluginexample",
                        "function_name": "plugin_init_ok",
                    },
                }
            ]
            self.assertEqual(expected_load_data[0], data_sorted[2])

            expected_load_data = [
                {
                    "status": "FAIL",
                    "exception": "AttributeError",
                    "traceback": mock.ANY,
                    "plugin_id": "asgard-api-plugin-metrics-example-1",
                    "entrypoint": {
                        "module_name": "metricpluginexample",
                        "function_name": "plugin_init_wrong_return",
                    },
                }
            ]
            self.assertEqual(expected_load_data[0], data_sorted[3])
