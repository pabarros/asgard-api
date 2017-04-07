# encoding utf-8

import os
import base64

from marathon import MarathonClient

ENABLED = "1"

MARATHON_ENDPOINT = os.getenv("MARATHON_ENDPOINT", "http://127.0.0.1:8080")
MARATHON_CREDENTIALS = os.getenv("MARATHON_CREDENTIALS", "guest:guest")

MARATHON_AUTH_HEADER = "Basic {}".format(base64.b64encode(MARATHON_CREDENTIALS))

user, passw = MARATHON_CREDENTIALS.split(':')
marathon_client = MarathonClient([MARATHON_ENDPOINT], username=user, password=passw)

# Default enabled
FILTER_DNS_ENABLED = os.getenv("HOLLOWMAN_FILTER_DNS_ENABLE", "1") == "1"

def _build_cors_whitelist(env_value):
    if not env_value:
        return []
    return [_host.strip() for _host in env_value.split(",") if _host.strip()]

CORS_WHITELIST = _build_cors_whitelist(os.getenv("HOLLOWMAN_CORS_WHITELIST"))

REDIRECT_ROOTPATH_TO = os.getenv("HOLLOWMAN_REDIRECT_ROOTPATH_TO", "/v2/apps")
