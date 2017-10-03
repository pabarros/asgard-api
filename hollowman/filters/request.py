# encoding: utf-8

import os
import json

from hollowman.filters.dns import DNSRequestFilter
from hollowman.filters.trim import TrimRequestFilter
from hollowman.filters.default_scale import DefaultScaleRequestFilter
from hollowman.filters.base_constraint import BaseConstraintFilter
from hollowman.filters import Context
from hollowman.filters.forcepull import ForcePullFilter
from hollowman import conf

from marathon.models import MarathonApp

DISABLER_ENV_VAR_NAME   = "HOLLOWMAN_FILTER_{filter_name}_DISABLE"
DISABLER_LABEL_NAME     = "hollowman.filter.{filter_name}.disable"

def _build_filters_list():
    _all_filters = [
        TrimRequestFilter(),
        ForcePullFilter(),
        BaseConstraintFilter(),
        DefaultScaleRequestFilter(),
        DNSRequestFilter(),
    ]

    _enabled_filters = []

    for f in _all_filters:
        env_name = DISABLER_ENV_VAR_NAME.format(filter_name=f.name)
        if os.getenv(env_name.upper()) is None:
            _enabled_filters.append(f)

    return _enabled_filters

def _get_ctx(request):
    """
    :rtype: hollowman.filters.Context
    """
    return Context(marathon_client=conf.marathon_client, request=request)

class RequestFilter(object):

    @staticmethod
    def check_filter_enabled(ctx, request, request_filter):
        """
        :param ctx:
        :type ctx: hollowman.filters.Context

        :param request:
        :type request: hollowman.hollowman_flask.HollowmanRequest

        :param request_filter:
        :type request_filter: hollowman.filters.BaseFilter
        """
        original_app = request_filter.get_original_app(ctx)

        request_as_json = request.get_json() if (request.is_json and request.data) else {}
        some_label_was_modified = "labels" in request_as_json

        request_app = MarathonApp.from_json(request_as_json)

        disable_label = DISABLER_LABEL_NAME.format(filter_name=request_filter.name)

        if disable_label not in request_app.labels:
            if not some_label_was_modified:
                return disable_label not in original_app.labels
            else:
                return True

    @staticmethod
    def dispatch(request):
        ctx = _get_ctx(request)
        for _request_filter in _filters:
            if RequestFilter.check_filter_enabled(ctx, request, _request_filter):
                _request_filter.run(ctx)
        return ctx.request

_filters = _build_filters_list()
