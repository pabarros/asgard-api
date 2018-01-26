
from hollowman.plugins import load_entrypoint_group, load_all_metrics_plugins
from hollowman.app import application

import unittest

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
        load_all_metrics_plugins(application)
        with application.test_client() as client:
            response = client.get("/_cat/metrics/asgard-api-plugin-metrics-example-1/ping")
            self.assertEqual(200, response.status_code)
            self.assertEqual(b"Metrics Plugin Example 1 OK", response.data)

