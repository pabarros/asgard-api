# encoding: utf-8

from hollowman.filters.dns import DNSRequestFilter
from hollowman.filters.trim import TrimRequestFilter
from hollowman.filters.default_scale import DefaultScaleRequestFilter
from hollowman.filters.base_constraint import BaseConstraintFilter
from hollowman.filters.appname import AddAppNameFilter
from hollowman.filters import Context
from hollowman.filters.forcepull import ForcePullFilter
from hollowman.conf import marathon_client

_filters = [
    DNSRequestFilter(),
    TrimRequestFilter(),
    ForcePullFilter(),
    BaseConstraintFilter(),
    DefaultScaleRequestFilter(),
    AddAppNameFilter(),
]

class RequestFilter(object):

    @staticmethod
    def dispatch(request):
        ctx = Context(marathon_client=marathon_client, request=request)
        for _request_filter in _filters:
            _request_filter.run(ctx)
        return ctx.request
