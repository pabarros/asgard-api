from typing import Iterable
from flask import Response as FlaskResponse, request
import json

from hollowman.filters.basicconstraint import BasicConstraintFilter
from marathon.models import MarathonDeployment, MarathonQueueItem
from marathon.models.task import MarathonTask

from hollowman.marathonapp import SieveMarathonApp

from hollowman.filters.uri import AddURIFilter
from hollowman.filters.trim import TrimRequestFilter
from hollowman.filters.forcepull import ForcePullFilter
from hollowman.filters.appname import AddAppNameFilter
from hollowman.filters.namespace import NameSpaceFilter
from hollowman.hollowman_flask import OperationType, FilterType, HollowmanRequest
from hollowman.filters.owner import AddOwnerConstraintFilter
from hollowman.filters.defaultscale import DefaultScaleFilter
from hollowman.filters.incompatiblefields import IncompatibleFieldsFilter
from hollowman.filters.labels import LabelsFilter
from hollowman.http_wrappers.response import Response
from hollowman.http_wrappers.base import RequestResource


FILTERS_PIPELINE = {
    FilterType.REQUEST: {
        OperationType.READ: (
        ),

        OperationType.WRITE: (
            NameSpaceFilter(),
            AddURIFilter(),
            DefaultScaleFilter(),
            ForcePullFilter(),
            TrimRequestFilter(),
            AddAppNameFilter(),
            BasicConstraintFilter(),
            AddOwnerConstraintFilter(),
            IncompatibleFieldsFilter(),
            LabelsFilter(),
        )
    },
    FilterType.RESPONSE: {
        OperationType.READ: (
            NameSpaceFilter(),
        ),
        OperationType.WRITE: (
            NameSpaceFilter(),
        )
    }
}

def _get_filter_callable_name(request, operation):
    func = lambda user, request_obj, original_obj: request_obj
    if request.is_tasks_request():
        method_name = f"{operation.value}_task"
    else:
        method_name = operation.value

    return method_name

def dispatch(user, request, filters_pipeline=FILTERS_PIPELINE[FilterType.REQUEST], filter_method_name_callback=_get_filter_callable_name) -> HollowmanRequest:
    """
    :type user: User
    :type request: http_wrappers.Request
    :type filters_pipeline: Dict[OperationType, Iterable[BaseFilter]]

    todo: (user, request_app, original_app) podem ser refatorados em uma classe de domínio
    """

    filtered_apps = []

    for operation in request.request.operations:
        for request_app, original_app in request.split():
            if _dispatch(request,
                      filters_pipeline[operation],
                      filter_method_name_callback(request, operation),
                      request_app, original_app):
                filtered_apps.append((request_app, original_app))

    return request.join(filtered_apps)

def _get_callable_if_exist(filter_, method_name):
    if hasattr(filter_, method_name):
        return getattr(filter_, method_name)
    return lambda *args: True

def _dispatch(request_or_response, filters_pipeline, filter_method_name, *filter_args):
    for filter_ in filters_pipeline:
        func = _get_callable_if_exist(filter_, filter_method_name)
        if func(request_or_response.request.user, *filter_args):
            continue
        return False
    return True

def dispatch_response_pipeline(user, response: Response, filters_pipeline=FILTERS_PIPELINE[FilterType.RESPONSE]) -> FlaskResponse:

    FILTERS_METHOD_NAMES = {
        RequestResource.APPS: "response",
        RequestResource.GROUPS: "response_group",
        RequestResource.DEPLOYMENTS: "response_deployment",
        RequestResource.TASKS: "response_task",
        RequestResource.QUEUE: "response_queue",
    }

    if any([response.is_app_request(),
            response.is_group_request(),
            response.is_deployment(),
            response.is_tasks_request(),
            response.is_queue_request()
            ]):
        return dispatch(user, response, filters_pipeline, lambda *args: FILTERS_METHOD_NAMES[response.request_resource])

