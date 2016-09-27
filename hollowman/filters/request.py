#encoding: utf-8

from hollowman.filters.dns import DNSRequestFilter 


_filters = [DNSRequestFilter()]

class RequestFilter(object):
  
  @staticmethod
  def dispatch(request):
      next_ = request
      for _request_filter in _filters:
          next_ = _request_filter.run(next_)
      return next_
