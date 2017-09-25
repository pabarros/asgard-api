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

    def __init__(self, request: HollowmanRequest):
        self.request = request
        self.marathon_client = conf.marathon_client

    def is_read_request(self) -> bool:
        return OperationType.READ in self.request.operations

    def is_app_request(self):
        """
        It's a request at /v2/apps/* ?
        """
        return self.request.path.startswith(self.app_path_prefix)

    def is_list_apps_request(self):
        """
        It's a request at /v2/apps/$ ?
        """
        return self.is_app_request() and self.app_id is None

    def is_group_request(self):
        """
        It's a request at /v2/groups/* ?
        """
        return self.request.path.startswith(self.group_path_prefix)

    @property
    def app_id(self) -> str:
        """
        self.request.path = '/v2/apps//marathon/app/id' -> '//marathon/app/id'
        self.request.path = '/v2/apps/marathon/app/id' -> '/marathon/app/id'


        Marathon's api accept both double or single slashes at the beginning

        """
        if not self.is_app_request():
            raise ValueError("Not a valid /v2/apps path")

        split_ = self.request.path.split('/')
        api_paths = [
            'restart',
            'tasks',
            'versions',
        ]
        locations = [split_.index(path) for path in api_paths if path in split_]
        cut_limit = min(locations or [len(split_)])
        # Removes every path after the app name
        split_ = split_[:cut_limit]

        # Removes evey empty path
        split_ = [part for part in split_ if part]
        return '/'.join(split_).replace('v2/apps', '') or None

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
                app = self.marathon_client.get_app(self.app_id)
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
