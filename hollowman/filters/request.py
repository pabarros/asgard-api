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
    lowercase_envvars = [envvar.lower() for envvar in os.environ]

    for f in _all_filters:
        if conf.ConfHelper.get_filter_disable_variable(f) not in lowercase_envvars:
            _enabled_filters.append(f)

    return _enabled_filters

def _get_ctx(request):
    """
    :rtype: hollowman.filters.Context
    """
    return Context(marathon_client=conf.marathon_client, request=request)

class RequestFilter(object):

    @staticmethod
    def check_filter_disable(ctx, request, request_filter):
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
        disable_variable = conf.ConfHelper.get_filter_disable_variable(request_filter)

        return disable_variable in request_app.env or \
                disable_variable in original_app.labels

    @staticmethod
    def dispatch(request):
        ctx = _get_ctx(request)
        for _request_filter in _filters:
            if not RequestFilter.check_filter_disable(ctx, request, _request_filter):
                _request_filter.run(ctx)
        return ctx.request

_filters = _build_filters_list()
