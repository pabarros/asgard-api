# encoding utf-8

import os
import base64

from marathon import MarathonClient

MARATHON_ENDPOINT = os.getenv("MARATHON_ENDPOINT", "http://127.0.0.1:8080")
MARATHON_CREDENTIALS = os.getenv("MARATHON_CREDENTIALS", "guest:guest")

MARATHON_AUTH_HEADER = "Basic {}".format(base64.b64encode(MARATHON_CREDENTIALS))

user, passw = MARATHON_CREDENTIALS.split(':')
marathon_client = MarathonClient([MARATHON_ENDPOINT], username=user, password=passw)

def _build_cors_whitelist(env_value):
    if not env_value:
        return []
    return [_host.strip() for _host in env_value.split(",") if _host.strip()]

CORS_WHITELIST = _build_cors_whitelist(os.getenv("HOLLOWMAN_CORS_WHITELIST"))

REDIRECT_ROOTPATH_TO = os.getenv("HOLLOWMAN_REDIRECT_ROOTPATH_TO", "/v2/apps")
GOOGLE_OAUTH2_CLIENT_ID = os.getenv("HOLLOWMAN_GOOGLE_OAUTH2_CLIENT_ID", "client_id")
GOOGLE_OAUTH2_CLIENT_SECRET = os.getenv("HOLLOWMAN_GOOGLE_OAUTH2_CLIENT_SECRET", "client_secret")

SECRET_KEY = os.getenv("HOLLOWMAN_SECRET_KEY")
REDIRECT_AFTER_LOGIN = os.getenv("HOLLOWMAN_REDIRECT_AFTER_LOGIN")

HOLLOWMAN_DB_URL = os.getenv("HOLLOWMAN_DB_URL", "sqlite://")

