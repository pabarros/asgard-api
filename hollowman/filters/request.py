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

def _build_filters_list():
    _all_enabled_filters = []

    if conf.FILTER_DNS_ENABLED:
        _all_enabled_filters.append(DNSRequestFilter())

    _other_filters = [
        TrimRequestFilter(),
        ForcePullFilter(),
        BaseConstraintFilter(),
        DefaultScaleRequestFilter(),
        AddAppNameFilter(),
    ]

    _all_enabled_filters.extend(_other_filters)
    return _all_enabled_filters

def _get_ctx(request):
    return Context(marathon_client=conf.marathon_client, request=request)

_filters = _build_filters_list()

class RequestFilter(object):

    @staticmethod
    def dispatch(request):
        ctx = _get_ctx(request)
        for _request_filter in _filters:
            _request_filter.run(ctx)
        return ctx.request
