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
    filtered_apps = []
    for request_app, app in request.split():
        filtered_request_app = dispatch(operations=request.request.operations,
                                        user=_get_user_from_request(request.request),
                                        request_app=request_app,
                                        app=app)
        filtered_apps.append((filtered_request_app, app))

    joined_request = request.join(filtered_apps)
    response = upstream_request(joined_request, run_filters=False)

    if not request.is_write_request() and response.status_code == HTTPStatus.OK:
        response_wrapper = http_wrappers.Response(request.request, response)
        final_response = dispatch_response_pipeline(user=_get_user_from_request(request.request),
                                                   response=response_wrapper)
        return final_response

    return response


def _get_user_from_request(request):
    try:
        return request.user
    except:
        return None
