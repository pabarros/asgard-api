from typing import Iterable
from flask import Response as FlaskResponse
import json

from hollowman.marathonapp import SieveMarathonApp

from hollowman.filters.trim import TrimRequestFilter
from hollowman.filters.forcepull import ForcePullFilter
from hollowman.filters.appname import AddAppNameFilter
from hollowman.filters.namespace import NameSpaceFilter
from hollowman.hollowman_flask import OperationType, FilterType
from hollowman.filters.owner import AddOwnerConstraintFilter
from hollowman.http_wrappers.response import Response


FILTERS_PIPELINE = {
    FilterType.REQUEST: {
        OperationType.READ: (
        ),

        OperationType.WRITE: (
            ForcePullFilter(),
            TrimRequestFilter(),
            AddAppNameFilter(),
            AddOwnerConstraintFilter(),
        )
    },
    FilterType.RESPONSE: (
        AddAppNameFilter(),
        NameSpaceFilter(),
    )
}


def dispatch(operations, user, request_app, app,
             filters_pipeline=FILTERS_PIPELINE[FilterType.REQUEST]) -> SieveMarathonApp:
    """
    :type operations: Iterable[OperationType]
    :type request_app: MarathonApp
    :type app: MarathonApp
    :type filters_pipeline: Dict[OperationType, Iterable[BaseFilter]]

    todo: (user, request_app, app) podem ser refatorados em uma classe de domínio
    """
    for operation in operations:
        for filter_ in filters_pipeline[operation]:
            func = getattr(filter_, operation.value)
            request_app = func(user, merge_marathon_apps(base_app=app, modified_app=request_app), app)

    return request_app


def dispatch_response_pipeline(user, response: Response, filters_pipeline=FILTERS_PIPELINE[FilterType.RESPONSE]) -> FlaskResponse:
    filtered_response_apps = []
    for response_app, original_app in response.split():
        filtered_app = response_app
        for filter_ in filters_pipeline:
            filtered_app = filter_.response(user, filtered_app, original_app)

        if user:
            if original_app.id.startswith("/{}/".format(user.current_account.namespace)):
                filtered_response_apps.append((filtered_app, original_app))
        else:
            filtered_response_apps.append((filtered_app, original_app))

    return response.join(filtered_response_apps)

def merge_marathon_apps(base_app, modified_app):
    merged = base_app.json_repr(minimal=False)
    merged.update(modified_app.json_repr(minimal=True))
    return SieveMarathonApp.from_json(merged)
