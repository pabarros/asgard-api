import json
from typing import Iterable, Tuple

import re
from marathon import MarathonApp
from marathon.exceptions import NotFoundError
from marathon.util import MarathonMinimalJsonEncoder

from hollowman import conf
from hollowman.hollowman_flask import HollowmanRequest, OperationType


class RequestParser:
    Apps = Iterable[Tuple[MarathonApp, MarathonApp]]
    json_encoder = MarathonMinimalJsonEncoder

    app_path_prefix = '/v2/apps'
    group_path_prefix = '/v2/groups'
    marathon_path_re = r'^\/v2\/[a-z]+(\/.+)'

    def __init__(self, request: HollowmanRequest):
        self.request = request
        self.marathon_client = conf.marathon_client

    def is_read_request(self) -> bool:
        return OperationType.READ in self.request.operations

    def is_app_request(self):
        return self.request.path.startswith(self.app_path_prefix)

    def is_list_apps_request(self):
        return self.is_app_request() and self.path is None

    def is_group_request(self):
        return self.request.path.startswith(self.group_path_prefix)

    @property
    def path(self) -> str:
        """
        self.request.path = '/v2/apps//marathon/app/id' -> '//marathon/app/id'
        self.request.path = '/v2/apps/marathon/app/id' -> '/marathon/app/id'


        Marathon's api accept both double or single slashes at the beginning

        """
        matches = re.match(self.marathon_path_re, self.request.path)
        if matches:
            return matches.groups()[0]

    def split(self) -> Apps:
        if self.is_group_request():
            raise NotImplementedError()

        if self.is_read_request():
            if self.is_list_apps_request():
                apps = self.marathon_client.list_apps()
                for app in apps:
                    yield MarathonApp(), app
                return
            else:
                app = self.marathon_client.get_app(self.path)
                yield MarathonApp(), app
                return

        data = self.request.get_json()
        if not isinstance(data, list):
            data = [data]

        for app in data:
            request_app = MarathonApp.from_json(app)

            try:
                app = self.marathon_client.get_app(request_app.id)
            except NotFoundError:
                app = MarathonApp()

            yield request_app, app

    def join(self, apps: Apps) -> HollowmanRequest:
        if self.is_group_request():
            raise NotImplementedError()

        if self.is_read_request() and self.is_app_request():
            """
            OperationType.READ derived request filters are 
            readonly and dont manipulate the request
            """
            return self.request

        apps_json_repr = [request_app.json_repr(minimal=True)
                          for request_app, _ in apps]
        request = HollowmanRequest(environ=self.request.environ, shallow=True)
        request.data = json.dumps(apps_json_repr, cls=self.json_encoder)
        return request
