from tracemalloc import BaseFilter
from typing import Iterable, Dict

import http_wrappers
from hollowman.filters.basicconstraint import BasicConstraintFilter
from marathon.models import MarathonDeployment, MarathonQueueItem
from marathon.models.task import MarathonTask

from hollowman.marathonapp import AsgardApp

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
from hollowman.filters.transformjson import TransformJSONFilter

FILTERS_METHOD_NAMES = {
    RequestResource.APPS: "response",
    RequestResource.GROUPS: "response_group",
    RequestResource.DEPLOYMENTS: "response_deployment",
    RequestResource.TASKS: "response_task",
    RequestResource.QUEUE: "response_queue",
}

FILTERS_PIPELINE = {
    FilterType.REQUEST: {
        OperationType.READ: (
        ),

        OperationType.WRITE: (
            NameSpaceFilter(),
            TransformJSONFilter(),
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
            TransformJSONFilter(),
        ),
        OperationType.WRITE: (
            NameSpaceFilter(),
            TransformJSONFilter(),
        )
    }
}


def _get_filter_callable_name(request, operation):
    if request.is_tasks_request():
        method_name = f"{operation.value}_task"
    else:
        method_name = operation.value

    return method_name


def dispatch(user,
             request: http_wrappers.Request,
             filters_pipeline: Dict[OperationType, Iterable[BaseFilter]] = FILTERS_PIPELINE[FilterType.REQUEST],
             filter_method_name_callback=_get_filter_callable_name) -> HollowmanRequest:
    # TODO: (user, request_app, original_app) podem ser refatorados em uma classe de domínio

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


def _dispatch(request_or_response, filters_pipeline, filter_method_name, *filter_args):
    for filter_ in filters_pipeline:
        func = _get_callable_if_exist(filter_, filter_method_name)
        if not func or func(request_or_response.request.user, *filter_args):
            continue
        return False
    return True
