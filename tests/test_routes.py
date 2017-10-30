import unittest
from mock import patch
from flask import Response

import hollowman.routes
from hollowman.app import application
from hollowman import decorators

class RoutesTest(unittest.TestCase):

    def setUp(self):
        self.enforce_auth = patch.multiple(decorators, HOLLOWMAN_ENFORCE_AUTH=False)
        self.enforce_auth.start()

        self.proxy_mock_patcher = patch.object(hollowman.routes, 'raw_proxy')
        self.proxy_mock = self.proxy_mock_patcher.start()
        self.proxy_mock.return_value = Response(status=200)

    def tearDown(self):
        self.enforce_auth.stop()
        self.proxy_mock_patcher.stop()

    def test_v2_deployments(self):
        with application.test_client() as client:
            client.get("/v2/deployments")
            client.get("/v2/deployments/uuid")
            client.delete("/v2/deployments/uuid")

            self.assertEqual(3, self.proxy_mock.call_count)

    def test_v2_tasks(self):
        with application.test_client() as client:
            client.get("/v2/tasks")
            client.post("/v2/tasks/delete")
            self.assertEqual(2, self.proxy_mock.call_count)

    def test_v2_artifacts(self):
        with application.test_client() as client:
            client.get("/v2/artifacts")

            client.get("/v2/artifacts/etc/hosts")
            client.put("/v2/artifacts/etc/hosts")
            client.post("/v2/artifacts/etc/hosts")
            client.delete("/v2/artifacts/etc/hosts")

            client.get("/v2/artifacts//etc/hosts")
            client.put("/v2/artifacts//etc/hosts")
            client.post("/v2/artifacts//etc/hosts")
            client.delete("/v2/artifacts//etc/hosts")
        self.assertEqual(9, self.proxy_mock.call_count)

    def test_v2_info(self):
        with application.test_client() as client:
            client.get("/v2/info")
            self.assertEqual(1, self.proxy_mock.call_count)

    def test_v2_leader(self):
        with application.test_client() as client:
            client.get("/v2/leader")
            client.delete("/v2/leader")
            self.assertEqual(2, self.proxy_mock.call_count)

    def test_v2_queue(self):
        with application.test_client() as client:
            client.get("/v2/queue")

            client.get("/v2/queue/app/id/delay")
            client.delete("/v2/queue/app/id/delay")

            client.get("/v2/queue//app/id/delay")
            client.delete("/v2/queue//app/id/delay")
            self.assertEqual(5, self.proxy_mock.call_count)

    def test_v2_info(self):
        with application.test_client() as client:
            client.get("/v2/info")
            self.assertEqual(1, self.proxy_mock.call_count)

    def test_ping(self):
        with application.test_client() as client:
            client.get("/ping")
            self.assertEqual(1, self.proxy_mock.call_count)

    def test_metrics(self):
        with application.test_client() as client:
            client.get("/metrics")
            self.assertEqual(1, self.proxy_mock.call_count)

