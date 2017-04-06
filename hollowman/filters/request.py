# encoding: utf-8

import os

from hollowman.filters.dns import DNSRequestFilter
from hollowman.filters.trim import TrimRequestFilter
from hollowman.filters.default_scale import DefaultScaleRequestFilter
from hollowman.filters.base_constraint import BaseConstraintFilter
from hollowman.filters.appname import AddAppNameFilter
from hollowman.filters import Context
from hollowman.filters.forcepull import ForcePullFilter
from hollowman import conf

from marathon.models import MarathonApp

DISABLER_ENV_VAR_NAME = "HOLLOWMAN_FILTER_{filter_name}_ENABLE"

def _build_filters_list():
    _all_filters = [
        DNSRequestFilter(),
        TrimRequestFilter(),
        ForcePullFilter(),
        BaseConstraintFilter(),
        DefaultScaleRequestFilter(),
        AddAppNameFilter(),
    ]

    _enabled_filters = []

    for f in _all_filters:
        env_name = DISABLER_ENV_VAR_NAME.format(filter_name=f.name)
        if os.getenv(env_name.upper(), conf.ENABLED) == conf.ENABLED:
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
        request_app = MarathonApp(request.data if hasattr(request, "data") else None)

        return conf.ConfHelper.is_filter_locally_enabled(request_filter, original_app) or \
                conf.ConfHelper.is_filter_locally_enabled(request_filter, request_app)

    @staticmethod
    def dispatch(request):
        ctx = _get_ctx(request)
        for _request_filter in _filters:
            if RequestFilter.check_filter_enabled(ctx, request, _request_filter):
                _request_filter.run(ctx)
        return ctx.request

_filters = _build_filters_list()
