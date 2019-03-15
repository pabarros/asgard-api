import abc
from http import HTTPStatus
from typing import Optional

from flask import Response
from marathon.models import MarathonDeployment
from werkzeug.utils import cached_property

from hollowman import conf, http_wrappers, upstream
from hollowman.dispatcher import FILTERS_PIPELINE, dispatch
from hollowman.hollowman_flask import (
    FilterType,
    HollowmanRequest,
    OperationType,
)
from hollowman.http_wrappers.base import RequestResource
from hollowman.models import User

FILTERS_METHOD_NAMES = {
    RequestResource.APPS: "response",
    RequestResource.GROUPS: "response_group",
    RequestResource.DEPLOYMENTS: "response_deployment",
    RequestResource.TASKS: "response_task",
    RequestResource.QUEUE: "response_queue",
}


def upstream_request(request: HollowmanRequest) -> Response:
    resp = upstream.replay_request(request)
    return Response(
        response=resp.content,
        status=resp.status_code,
        headers=dict(resp.headers),
    )


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
        response = http_wrappers.Response(
            self.wrapped_request.request, response
        )
        return dispatch(
            self.user,
            response,
            filters_pipeline=FILTERS_PIPELINE[FilterType.RESPONSE],
            filter_method_name_callback=lambda response, *args: FILTERS_METHOD_NAMES[
                response.request_resource
            ],
        )

    def handle(self) -> Response:
        response = upstream_request(self.wrapped_request.request)

        if self._should_apply_response_filters():
            return self._apply_response_filters(response)

        return response


def new(request: http_wrappers.Request) -> Response:

    filtered_request = dispatch(user=request.request.user, request=request)

    upstream_response = upstream_request(filtered_request)

    if upstream_response.status_code == HTTPStatus.OK:
        response = http_wrappers.Response(request.request, upstream_response)
        return dispatch(
            request.request.user,
            response,
            filters_pipeline=FILTERS_PIPELINE[FilterType.RESPONSE],
            filter_method_name_callback=lambda response, *args: FILTERS_METHOD_NAMES[
                response.request_resource
            ],
        )

    return upstream_response
