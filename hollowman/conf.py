# encoding utf-8

import os
import base64

from marathon import MarathonClient

MARATHON_ENDPOINT = os.getenv("MARATHON_ENDPOINT", "http://127.0.0.1:8080")
MARATHON_CREDENTIALS = os.getenv("MARATHON_CREDENTIALS", "guest:guest")

MARATHON_AUTH_HEADER = "Basic {}".format(
    base64.b64encode(MARATHON_CREDENTIALS))

user, passw = MARATHON_CREDENTIALS.split(':')
marathon_client = MarathonClient([MARATHON_ENDPOINT], username=user, password=passw)

# Default enabled
FILTER_DNS_ENABLED = os.getenv("HOLLOWMAN_FILTER_DNS_ENABLE", "1") == "1"
