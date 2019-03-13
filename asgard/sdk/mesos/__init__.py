from http import HTTPStatus

import aiohttp
import requests

from asgard.http.client import http_client
from asgard.sdk.options import get_option


def get_mesos_leader_address():
    for mesos_address in get_option("MESOS", "ADDRESS"):
        try:
            response = requests.get(
                f"{mesos_address}/redirect", timeout=2, allow_redirects=False
            )
            if response.headers.get("Location"):
                leader_ip = response.headers.get("Location").split("//")[1]
                # config.logger.debug({"action": "find-mesos-leader", "try-address": mesos_address, "exception": False, "leader-ip": leader_ip})
                return f"http://{leader_ip}"
        except requests.exceptions.ConnectionError as ConErr:
            pass
            # config.logger.debug({"action": "find-mesos-leader", "try-address": mesos_address, "exception": True})


async def leader_address():
    for mesos_address in get_option("MESOS", "ADDRESS"):
        try:
            async with http_client.get(
                f"{mesos_address}/redirect", allow_redirects=False
            ) as response:
                if response.headers.get("Location"):
                    leader_ip = response.headers.get("Location").split("//")[1]
                    return f"http://{leader_ip}"
        except aiohttp.client_exceptions.ServerTimeoutError as timeout_error:
            pass
        except aiohttp.client_exceptions.ClientConnectorError as connection_error:
            pass


def is_master_healthy(master_url):
    try:
        response = requests.get(
            f"{master_url}/health", timeout=2, allow_redirects=False
        )
        return response.status_code == HTTPStatus.OK
    except Exception:
        pass

    return False
