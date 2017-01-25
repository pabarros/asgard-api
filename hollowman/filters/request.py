# encoding: utf-8

from hollowman.filters.dns import DNSRequestFilter
from hollowman.filters.trim import TrimRequestFilter
from hollowman.filters.default_scale import DefaultScaleRequestFilter
from hollowman.filters import Context
from hollowman.conf import marathon_client

_ctx = Context(marathon_client=marathon_client)

_filters = [
    DNSRequestFilter(_ctx),
    TrimRequestFilter(_ctx),
    DefaultScaleRequestFilter(_ctx),
]

class RequestFilter(object):

    @staticmethod
    def dispatch(request):
        next_ = request
        for _request_filter in _filters:
            next_ = _request_filter.run(next_)
        return next_
