# encoding: utf-8

import requests
import sys
from hollowman import conf


def replay_request(request, destination_url):
    to_url = "{}{}".format(destination_url, request.path)
    params = [(key, value)
              for key, value in request.args.iteritems(multi=True)]
    headers = dict(request.headers)
    headers.pop("Content-Length", None)
    headers['Authorization'] = conf.MARATHON_AUTH_HEADER
    return getattr(requests, request.method.lower())(to_url, params=params, headers=headers, data=request.data)
