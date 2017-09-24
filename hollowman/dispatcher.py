from typing import Iterable

from marathon import MarathonApp

from hollowman.filters.dummy import DummyLogFilter
from hollowman.hollowman_flask import OperationType
from hollowman.log import logger


class InterruptPipelineException(Exception):
    def __init__(self, response_body: dict, status_code: int):
        self.response_body = response_body
        self.status_code = status_code


filters_pipeline = {
    OperationType.READ: (DummyLogFilter(),)
}


def dispatch(operations: Iterable[OperationType],
             user,
             request_app: MarathonApp,
             app: MarathonApp) -> MarathonApp:
    logger.debug(request_app)
    for operation in operations:
        for filter_ in filters_pipeline[operation]:
            func = getattr(filter_, operation.value)
            try:
                request_app = func(user, request_app, app)
            except KeyError:
                pass  # skip. Unintersting operation
    return request_app
