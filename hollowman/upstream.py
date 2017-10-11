# encoding: utf-8

import sys
import json

import requests

from hollowman import conf


def replay_request(request, destination_url):
    to_url = "{}{}".format(destination_url, request.path)
    params = [(key, value)
              for key, value in request.args.items(multi=True)]
    headers = dict(request.headers)
    headers.pop("Content-Length", None)
    headers['Authorization'] = conf.MARATHON_AUTH_HEADER
    method = request.method.lower()
    if method in ['put', 'post'] and request.is_json:
        request_data = json.loads(request.data)
        if isinstance(request_data, list):
            for data in request_data:
                _remove_keys(data)
        else:
            _remove_keys(request_data)
        request.data = json.dumps(request_data)
    upstream_response = getattr(requests, method)(to_url, params=params, headers=headers, data=request.data)
    upstream_response.headers.pop("Content-Encoding", None)
    upstream_response.headers.pop("Transfer-Encoding", None) # Marathon 1.3.x returns all responses gziped
    return upstream_response

def _remove_keys(data):
    data.pop("version", None)
    data.pop("fetch", None)

