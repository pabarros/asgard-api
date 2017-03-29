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

from marathon.models import app

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
        filter_disable_control_envvar = "{prefix}.{filter_name}.disable".format(
            prefix=RequestFilter.control_label_prefix,
            filter_name=f
        )
        if filter_disable_control_envvar not in [envvar.lower() for envvar in os.environ]:
            _enabled_filters.append(f)

    return _enabled_filters

def _get_ctx(request):
    """
    :rtype: hollowman.filters.Context
    """
    return Context(marathon_client=conf.marathon_client, request=request)

class RequestFilter(object):

    """
    Prefix for control labels used by Hollowman itself
    """
    control_label_prefix = "hollowman"

    @staticmethod
    def check_filter_disable(ctx, request, request_filter):
        """
        :param request_filter:
        :type request_filter: hollowman.filters.BaseFilter
        """
        original_app = request_filter.get_original_app(ctx)

        # disable all via env var on hollowman
        # check payload app for disabling too
        # check if all registered filters has .name

        return "{prefix}.{filter_name}.disable".format(
            prefix=RequestFilter.control_label_prefix,
            filter_name=request_filter.name.lower()
        ).strip() in original_app.labels

    @staticmethod
    def dispatch(request):
        ctx = _get_ctx(request)
        for _request_filter in _filters:
            if not RequestFilter.check_filter_disable(ctx, request, _request_filter):
                _request_filter.run(ctx)
        return ctx.request

_filters = _build_filters_list()
