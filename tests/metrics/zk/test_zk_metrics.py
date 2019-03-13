import json
import os
from unittest import TestCase
from unittest.mock import patch

from hollowman.app import application
from hollowman.metrics.zk import routes


class TestZKMetrics(TestCase):
    def setUp(self):
        self.send_command_patcher = patch.object(routes, "send_command")
        self.send_command_patcher.start()

        self.parse_stat_output_patcher = patch.object(
            routes, "parse_stat_output"
        )
        self.parse_stat_output_mock = self.parse_stat_output_patcher.start()

    def tearDown(self):
        self.send_command_patcher.stop()
        self.parse_stat_output_patcher.stop()

    def test_zk_metrics_server_not_found(self):
        with application.test_client() as client:
            res = client.get("/_cat/metrics/zk/1")
            self.assertEqual(404, res.status_code)
            self.assertEqual(b"{}", res.data)

    def test_zk_metrics_server_found(self):
        with application.test_client() as client:
            with patch.dict(os.environ, HOLLOWMAN_METRICS_ZK_ID_0="127.0.0.1"):
                expected_return = {"connections": 10, "is_leader": 0}
                self.parse_stat_output_mock.return_value = expected_return
                res = client.get("/_cat/metrics/zk/1")
                self.assertEqual(200, res.status_code)
                self.assertEqual(
                    expected_return, json.loads(res.data.decode("utf8"))
                )

    def test_zk_leader_with_leader(self):
        with application.test_client() as client:
            with patch.dict(
                os.environ,
                HOLLOWMAN_METRICS_ZK_ID_0="127.0.0.1",
                HOLLOWMAN_METRICS_ZK_ID_1="127.0.0.1",
                HOLLOWMAN_METRICS_ZK_ID_2="127.0.0.1",
            ):
                expected_return = [
                    {"mode": "follower"},
                    {"mode": "leader"},
                    {"mode": "follower"},
                ]
                self.parse_stat_output_mock.side_effect = expected_return
                res = client.get("/_cat/metrics/zk/leader")
                self.assertEqual(200, res.status_code)
                self.assertEqual(
                    {"leader": 2}, json.loads(res.data.decode("utf8"))
                )

    def test_zk_leader_no_leader(self):
        with application.test_client() as client:
            with patch.dict(
                os.environ,
                HOLLOWMAN_METRICS_ZK_ID_0="127.0.0.1",
                HOLLOWMAN_METRICS_ZK_ID_1="127.0.0.1",
                HOLLOWMAN_METRICS_ZK_ID_2="127.0.0.1",
            ):
                expected_return = [
                    {"mode": "follower"},
                    {"mode": "follower"},
                    {"mode": "follower"},
                ]
                self.parse_stat_output_mock.side_effect = expected_return
                res = client.get("/_cat/metrics/zk/leader")
                self.assertEqual(200, res.status_code)
                self.assertEqual(
                    {"leader": 0}, json.loads(res.data.decode("utf8"))
                )
