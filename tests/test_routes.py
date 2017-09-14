import unittest
from mock import patch

import hollowman.routes
from hollowman.app import application

class RoutesTest(unittest.TestCase):

    @patch.object(hollowman.routes, 'raw_proxy')
    def test_v2_deployments(self, proxy_mock):
        with application.test_client() as client:
            client.get("/v2/deployments")
            client.get("/v2/deployments/uuid")
            client.delete("/v2/deployments/uuid")
            self.assertEqual(3, proxy_mock.call_count)

    @patch.object(hollowman.routes, 'raw_proxy')
    def test_v2_groups(self, proxy_mock):
        with application.test_client() as client:
            client.get("/v2/groups") #delete/put/post/get
            client.post("/v2/groups") #delete/put/post/get
            client.put("/v2/groups") #delete/put/post/get
            client.delete("/v2/groups") #delete/put/post/get

            client.get("/v2/groups/versions") #get

            client.get("/v2/groups//infra") #get/post/put/delete
            client.post("/v2/groups//infra") #get/post/put/delete
            client.put("/v2/groups//infra") #get/post/put/delete
            client.delete("/v2/groups//infra") #get/post/put/delete

            client.get("/v2/groups/infra") #get/post/put/delete
            client.post("/v2/groups/infra") #get/post/put/delete
            client.put("/v2/groups/infra") #get/post/put/delete
            client.delete("/v2/groups/infra") #get/post/put/delete

            client.get("/v2/groups/infra/versions") #get
            client.get("/v2/groups//infra/versions") #get
        self.assertEqual(15, proxy_mock.call_count)

    @patch.object(hollowman.routes, 'raw_proxy')
    def test_v2_tasks(self, proxy_mock):
        with application.test_client() as client:
            client.get("/v2/tasks")
            client.post("/v2/tasks/delete")
            self.assertEqual(2, proxy_mock.call_count)

    @patch.object(hollowman.routes, 'raw_proxy')
    def test_v2_artifacts(self, proxy_mock):
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
        self.assertEqual(9, proxy_mock.call_count)

    @patch.object(hollowman.routes, 'raw_proxy')
    def test_v2_info(self, proxy_mock):
        with application.test_client() as client:
            client.get("/v2/info")
            self.assertEqual(1, proxy_mock.call_count)

    @patch.object(hollowman.routes, 'raw_proxy')
    def test_v2_leader(self, proxy_mock):
        with application.test_client() as client:
            client.get("/v2/leader")
            client.delete("/v2/leader")
            self.assertEqual(2, proxy_mock.call_count)

    @patch.object(hollowman.routes, 'raw_proxy')
    def test_v2_queue(self, proxy_mock):
        with application.test_client() as client:
            client.get("/v2/queue")

            client.get("/v2/queue/app/id/delay")
            client.delete("/v2/queue/app/id/delay")

            client.get("/v2/queue//app/id/delay")
            client.delete("/v2/queue//app/id/delay")
            self.assertEqual(5, proxy_mock.call_count)

    @patch.object(hollowman.routes, 'raw_proxy')
    def test_v2_info(self, proxy_mock):
        with application.test_client() as client:
            client.get("/v2/info")
            self.assertEqual(1, proxy_mock.call_count)

    @patch.object(hollowman.routes, 'raw_proxy')
    def test_ping(self, proxy_mock):
        with application.test_client() as client:
            client.get("/ping")
            self.assertEqual(1, proxy_mock.call_count)

    @patch.object(hollowman.routes, 'raw_proxy')
    def test_metrics(self, proxy_mock):
        with application.test_client() as client:
            client.get("/metrics")
            self.assertEqual(1, proxy_mock.call_count)

