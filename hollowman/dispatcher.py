from typing import Iterable

from hollowman.marathonapp import SieveMarathonApp

from hollowman.filters.trim import TrimRequestFilter
from hollowman.filters.forcepull import ForcePullFilter
from hollowman.filters.appname import AddAppNameFilter
from hollowman.hollowman_flask import OperationType, FilterType
from hollowman.filters.owner import AddOwnerConstraintFilter


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


def dispatch_response_pipeline(user, response, filters_pipeline=FILTERS_PIPELINE[FilterType.RESPONSE]):
#    filtered_response_apps = []
#    if request.is_app_request or request.is_list_apps_request():
#        for response_app, app in response_wrapper.split():
#            filtered_response_app = dispatch_response(user=_get_user_from_request(request.request),
#                              response_app=response_app,
#                              app=app)
#            filtered_response_apps.append((filtered_response_app, app))
#        import ipdb
#        ipdb.set_trace()
#        filtered_response_apps_ = [app for app in filtered_response_apps if app[0].id.startswith("/sieve")]
#        return response_wrapper.join(filtered_response_apps_)
    #for filter in filters_pipeline:
    #    response_app = filter.response(user, response_app, app)

    #return response_app
    return response.response


def merge_marathon_apps(base_app, modified_app):
    merged = base_app.json_repr(minimal=False)
    merged.update(modified_app.json_repr(minimal=True))
    return SieveMarathonApp.from_json(merged)
