import abc
from typing import Optional

from flask import Response
from http import HTTPStatus

from marathon.models import MarathonDeployment
from werkzeug.utils import cached_property

from hollowman.dispatcher import dispatch, dispatch_response_pipeline, \
    FILTERS_PIPELINE
from hollowman.hollowman_flask import HollowmanRequest, FilterType
from hollowman import upstream, conf, http_wrappers
from hollowman.hollowman_flask import OperationType
from hollowman.models import User


def upstream_request(request: HollowmanRequest, run_filters=True) -> Response:
    resp = upstream.replay_request(request, conf.MARATHON_ENDPOINT)
    return Response(response=resp.content,
                    status=resp.status_code,
                    headers=dict(resp.headers))


class RequestHandler(metaclass=abc.ABCMeta):
    def __init__(self, request: HollowmanRequest):
        self.wrapped_request = http_wrappers.Request(request)

    @cached_property
    def user(self) -> Optional[User]:
        try:
            return self.wrapped_request.request.user
        except:
            return None


class Deployments(RequestHandler):
    def _should_apply_response_filters(self) -> bool:
        return self.wrapped_request.is_read_request()

    def _apply_response_filters(self, response) -> Response:
        response_wrapper = http_wrappers.Response(self.wrapped_request.request,
                                                  response)
        return dispatch_response_pipeline(self.user, response_wrapper)

    def handle(self) -> Response:
        response = upstream_request(self.wrapped_request.request)

        if self._should_apply_response_filters():
            return self._apply_response_filters(response)

        return response


def new(request: http_wrappers.Request) -> Response:

    filtered_request = dispatch(user=request.request.user, request=request)

    upstream_response = upstream_request(filtered_request, run_filters=False)

    if upstream_response.status_code == HTTPStatus.OK:
        response_wrapper = http_wrappers.Response(request.request, upstream_response)
        filtered_response = dispatch_response_pipeline(user=request.request.user, response=response_wrapper)
        return filtered_response

    return upstream_response

