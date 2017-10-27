import json
from typing import Iterable, Dict

from marathon import MarathonApp, NotFoundError
from marathon.util import MarathonMinimalJsonEncoder

from hollowman.hollowman_flask import HollowmanRequest
from hollowman.http_wrappers.base import Apps, HTTPWrapper
from hollowman.marathon.group import SieveAppGroup


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

        if self.is_read_request():
            if self.is_list_apps_request():
                apps = self.marathon_client.list_apps()
                for app in apps:
                    yield MarathonApp(), app
                return
            elif self.is_group_request():
                self.group = self._get_original_group(self.request.user, self.group_id)
                for app in self.group.iterate_apps():
                    yield MarathonApp(), app
                return
            else:
                app = self._get_original_app(self.request.user, self.app_id)
                yield MarathonApp(), app
                return

        # Request is a WRITE
        if self.is_app_request():
            for app in self.get_request_data():
                request_app = MarathonApp.from_json(app)
                try:
                    app = self._get_original_app(self.request.user, self.app_id or request_app.id)
                except NotFoundError:
                    app = MarathonApp()

                yield request_app, app


    def _adjust_request_path_if_needed(self, request, modified_app_or_group):
        original_path = request.path.rstrip("/")
        if original_path.startswith("/v2/apps") and original_path != "/v2/apps":
            request.path = "/v2/apps{}".format(modified_app_or_group.id or self.app_id)
        if original_path.startswith("/v2/groups"):
            request.path = "/v2/groups{}".format(modified_app_or_group.id or (self.group_id or "/"))

    def join(self, apps: Apps) -> HollowmanRequest:
        request = HollowmanRequest(environ=self.request.environ, shallow=True)

        if self.is_read_request() and self.is_app_request():
            """
            OperationType.READ derived request filters are
            readonly and dont manipulate the request
            """
            request_app, original_app = apps[0]
            self._adjust_request_path_if_needed(self.request, original_app)
            return self.request

        if self.is_read_request() and self.is_group_request():
            self._adjust_request_path_if_needed(self.request, self.group)
            return self.request

        if self.is_list_apps_request():
            apps_json_repr = [request_app.json_repr(minimal=True)
                              for request_app, _ in apps]
        else:
            request_app, original_app = apps[0]
            self._adjust_request_path_if_needed(request, original_app)
            apps_json_repr = request_app.json_repr(minimal=True)

        request.data = json.dumps(apps_json_repr, cls=self.json_encoder)
        return request
