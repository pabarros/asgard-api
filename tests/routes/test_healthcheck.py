import json
from typing import Dict
from unittest import TestCase
from unittest.mock import patch

from responses import RequestsMock

from hollowman import conf
from hollowman.app import application


class HealthCheckTests(TestCase):
    def test_healthcheck_return_200_even_if_some_servers_are_down(self):
        marathon_addresses = [
            "http://invalid-host:8080",
            "http://172.30.0.1:8080",
            "http://172.31.0.1:8080",
        ]
        with application.test_client() as client, RequestsMock() as rsps, patch.multiple(
            conf, MARATHON_ADDRESSES=marathon_addresses
        ), patch.multiple(
            conf, MARATHON_LEADER=marathon_addresses[1]
        ):
            rsps.add(
                "GET",
                url=marathon_addresses[2] + "/ping",
                status=200,
                body="pong",
            )

            response = client.get("/healthcheck")
            self.assertEqual(200, response.status_code)

    def test_healthcheck_return_500_if_all_servers_down(self):
        marathon_addresses = [
            "http://invalid-host:8080",
            "http://172.30.0.1:8080",
            "http://172.31.0.1:8080",
        ]
        with application.test_client() as client, RequestsMock() as rsps, patch.multiple(
            conf, MARATHON_ADDRESSES=marathon_addresses
        ), patch.multiple(
            conf, MARATHON_LEADER=marathon_addresses[1]
        ):

            response = client.get("/healthcheck")
            self.assertEqual(500, response.status_code)
