# encoding utf-8

import os
import base64

from marathon import MarathonClient

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

"""
Prefix for control variables used by Hollowman itself. This is used to generate
variable names (labels, envvars, etc).
"""
variable_namespace = os.getenv('variable_namespace', 'hollowman').strip().lower()

class ConfHelper(object):

    @staticmethod
    def get_filter_variable_name(request_filter, variables = []):
        """
        This method must return the base name to be used on any
        control variable/label.

        Eg:
            For input: (<default_scale_filter>, ["disable"])
            Must return something like: "hollowman.default_scale.disable"

        :param request_filter: A request filter
        :type request_filter: hollowman.filters.BaseFilter

        :param variables: Variables to be used
        :type variables: list[str]
        """

        _variables = [v.lower().strip() for v in variables]

        return "".join(
            [variable_namespace, request_filter.name.strip()] + \
            _variables
        )

    @staticmethod
    def get_filter_disable_variable(request_filter):
        return ConfHelper.get_filter_variable_name(request_filter, ['disable'])
