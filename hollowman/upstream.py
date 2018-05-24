# encoding: utf-8

import sys
import json

import requests

from hollowman import conf
from hollowman.log import logger


def replay_request(request):
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
    upstream_response = _make_request(request.path, method, params=params, headers=headers, data=request.data)
    upstream_response.headers.pop("Content-Encoding", None)
    upstream_response.headers.pop("Transfer-Encoding", None) # Marathon 1.3.x returns all responses gziped
    return upstream_response

def _make_request(path, method, params=None, headers=None, data=None):
    for marathon_backend in [conf.MARATHON_LEADER] + conf.MARATHON_ADDRESSES:
        try:
            url = "{}{}".format(marathon_backend, path)
            response = getattr(requests, method)(url, params=params, headers=headers, data=data)
            leader_addr = response.headers.pop("X-Marathon-Leader", conf.MARATHON_ADDRESSES[0])
            conf.MARATHON_LEADER = leader_addr
            logger.debug({"new_leader": conf.MARATHON_LEADER, "talked_to": marathon_backend})
            return response
        except requests.exceptions.ConnectionError as e:
            pass
    raise Exception("No Marathon servers found")

def _remove_keys(data):
    data.pop("version", None)
    data.pop("fetch", None)
    data.pop("secrets", None)

