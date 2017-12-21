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


FILTERS_PIPELINE = {
    FilterType.REQUEST: {
        OperationType.READ: (
        ),

        OperationType.WRITE: (
            AddURIFilter(),
            DefaultScaleFilter(),
            NameSpaceFilter(),
            ForcePullFilter(),
            TrimRequestFilter(),
            AddAppNameFilter(),
            BasicConstraintFilter(),
            AddOwnerConstraintFilter(),
            IncompatibleFieldsFilter(),
            LabelsFilter(),
        )
    },
    FilterType.RESPONSE: (
        NameSpaceFilter(),
        IncompatibleFieldsFilter(),
    )
}

def _get_filter_callable(request, operation, filter_):
    func = lambda user, request_obj, original_obj: request_obj
    if request.is_tasks_request():
        method_name = f"{operation.value}_task"
    else:
        method_name = operation.value

    if hasattr(filter_, method_name):
        func = getattr(filter_, method_name)
    return func

def dispatch(user, request, filters_pipeline=FILTERS_PIPELINE[FilterType.REQUEST]) -> HollowmanRequest:
    """
    :type user: User
    :type request: http_wrappers.Request
    :type filters_pipeline: Dict[OperationType, Iterable[BaseFilter]]

    todo: (user, request_app, original_app) podem ser refatorados em uma classe de domínio
    """

    filtered_apps = []

    for operation in request.request.operations:
        for request_app, original_app in request.split():
            _dispatch(request,
                      filters_pipeline[operation],
                      operation,
                      _get_filter_callable,
                      request_app, original_app)
            filtered_apps.append((request_app, original_app))

    return request.join(filtered_apps)

def _dispatch(request, filters_pipeline, operation, get_filter_callable_callback, *filter_args):
    for filter_ in filters_pipeline:
        func = get_filter_callable_callback(request, operation, filter_)
        if func:
            func(request.request.user, *filter_args)

def _get_response_callable_app_request(request, operation, filter_):
    if hasattr(filter_, "response"):
        return getattr(filter_, "response")

def dispatch_response_pipeline(user, response: Response, filters_pipeline=FILTERS_PIPELINE[FilterType.RESPONSE]) -> FlaskResponse:
    if response.is_app_request():
        filtered_response_apps = []
        for response_app, original_app in response.split():
            _dispatch(response, filters_pipeline, None, _get_response_callable_app_request, response_app)

            if original_app.id.startswith("/{}/".format(user.current_account.namespace)):
                filtered_response_apps.append((response_app, original_app))

        return response.join(filtered_response_apps)
    elif response.is_group_request():
        filtered_response_groups = []
        for response_group, original_group in response.split():
            filtered_group = response_group
            for filter_ in filters_pipeline:
                if hasattr(filter_, "response_group"):
                    filter_.response_group(user, filtered_group)
            filtered_response_groups.append((filtered_group, original_group))
        return response.join(filtered_response_groups)
    elif response.is_deployment():
        content = json.loads(response.response.data)
        deployments = (MarathonDeployment.from_json(deploy) for deploy in content)

        filtered_deployments = []
        for deployment in deployments:
            # Não teremos deployments que afetam apps de múltiplos namespaces,
            # por isos podemos olhar apenas umas das apps.
            original_affected_apps_id = deployment.affected_apps[0]
            for filter_ in filters_pipeline:
                if hasattr(filter_, "response_deployment"):
                    filter_.response_deployment(user, deployment)
            if original_affected_apps_id.startswith("/{}/".format(user.current_account.namespace)):
                filtered_deployments.append(deployment)

        return FlaskResponse(
            response=json.dumps(filtered_deployments, cls=Response.json_encoder),
            status=response.response.status,
            headers=response.response.headers
        )
    elif response.is_queue_request():
        queue_data = json.loads(response.response.data)
        current_namespace = user.current_account.namespace
        filtered_queue_data = []
        queued_apps = (MarathonQueueItem.from_json(queue_item) for queue_item in queue_data['queue'])
        for queued_app in queued_apps:
            if queued_app.app.id.startswith("/{}".format(current_namespace)):
                queued_app.app.id = queued_app.app.id.replace("/{}".format(current_namespace), "")
                filtered_queue_data.append(queued_app)

        return FlaskResponse(
            response=json.dumps({"queue": filtered_queue_data}, cls=Response.json_encoder),
            status=response.response.status,
            headers=response.response.headers
        )
    elif response.is_tasks_request():
        content = json.loads(response.response.data)
        filtered_tasks = content
        try:
            tasks = (MarathonTask.from_json(task) for task in content['tasks'])

            filtered_tasks = []
            for task in tasks:
                task_original_idd = task.id
                for filter_ in filters_pipeline:
                    if hasattr(filter_, "response_task"):
                        filter_.response_task(user, task)

                if task_original_idd.startswith(f"{user.current_account.namespace}_"):
                    filtered_tasks.append((task, task))
        except KeyError:
            # resposne sem lista de task, retornamos sem mexer
            return response.response

        return response.join(filtered_tasks)

