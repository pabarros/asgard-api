import json
from typing import Iterable, Dict

from marathon import MarathonApp, NotFoundError
from marathon.util import MarathonMinimalJsonEncoder

from hollowman.hollowman_flask import HollowmanRequest
from hollowman.http_wrappers.base import Apps, HTTPWrapper


class Request(HTTPWrapper):
    json_encoder = MarathonMinimalJsonEncoder

    app_path_prefix = '/v2/apps'
    group_path_prefix = '/v2/groups'

    def __init__(self, request: HollowmanRequest):
        self.request = request

    def get_request_data(self) -> Iterable[Dict]:
        if not self.request.data:
            return [{}]

        data = self.request.get_json()
        """
        Matrathon's UI POST request to '/v2/apps/*/restart' contains a body
        with `{"force": (true|false)}` which isn't compatible with `MarathonApp`
        interface and marathons api, and should be removed.
        """
        if not isinstance(data, list):
            data.pop('force', None)
            return [data]
        return data

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

        for app in self.get_request_data():
            request_app = MarathonApp.from_json(app)
            try:
                app = self.marathon_client.get_app(self.app_id or request_app.id)
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
        if self.is_list_apps_request():
            apps_json_repr = [request_app.json_repr(minimal=True)
                              for request_app, _ in apps]
        else:
            request_app, _ = apps[0]
            apps_json_repr = request_app.json_repr(minimal=True)

        request = HollowmanRequest(environ=self.request.environ, shallow=True)
        request.data = json.dumps(apps_json_repr, cls=self.json_encoder)
        return request
