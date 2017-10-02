from typing import Iterable

from marathon import MarathonApp

from hollowman.filters.dummy import DummyLogFilter
from hollowman.filters.trim import TrimEnvvarsFilter
from hollowman.hollowman_flask import OperationType


FILTERS_PIPELINE = {
    OperationType.READ: (
        DummyLogFilter(),
    ),
    OperationType.WRITE: (
        DummyLogFilter(),
        TrimEnvvarsFilter()
    )
}


def dispatch(operations, user, request_app, app,
             filters_pipeline=FILTERS_PIPELINE) -> MarathonApp:
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
            request_app = func(user, request_app, app)

    return request_app
