from typing import Iterable

from marathon import MarathonApp

from hollowman.filters.dummy import DummyLogFilter
from hollowman.hollowman_flask import HollowmanRequest, OperationType


class InterruptPipelineException(Exception):
    def __init__(self, response_body: dict, status_code: int):
        self.response_body = response_body
        self.status_code = status_code


class RequestParser:
    def __init__(self, request: HollowmanRequest):
        self.request = request


filters_pipeline = {
    OperationType.READ: (DummyLogFilter(),)
}


def dispatch(self,
             operations: Iterable[OperationType],
             user,
             request_app: MarathonApp,
             app: MarathonApp):
    for operation in operations:
        for filter_ in filters_pipeline[operation]:
            func = getattr(filter_, operation)
            try:
                request_app = func(user, request_app, app)
            except InterruptPipelineException as e:
                # Usamos a exception para criar a response ou
                # retornar os dados para que alguém crie
                pass
            except KeyError:
                # skip. Unintersting operation
                pass
            except Exception:
                # erros de programação que vão retornar um 500
                pass
