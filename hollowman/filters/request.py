# encoding: utf-8

from hollowman.filters.dns import DNSRequestFilter
from hollowman.filters.trim import TrimEnvVarsRequestFilter
from hollowman.filters.default_scale import DefaultScaleRequestFilter


_filters = [
    DNSRequestFilter(),
    TrimEnvVarsRequestFilter(),
    DefaultScaleRequestFilter(),
]

class RequestFilter(object):

    @staticmethod
    def dispatch(request):
        next_ = request
        for _request_filter in _filters:
            next_ = _request_filter.run(next_)
        return next_
