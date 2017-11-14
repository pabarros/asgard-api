import json
from typing import Iterable, Dict

from marathon import MarathonApp, NotFoundError
from marathon.util import MarathonMinimalJsonEncoder
from marathon.models.group import MarathonGroup

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
            elif self.is_queue_request():
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
        original_path_parts = original_path.split("/")
        if original_path.startswith("/v2/apps") and original_path != "/v2/apps":
            app_id = modified_app_or_group.id or self.app_id
            last_app_id_part = app_id.split("/")[-1]
            last_part_position = original_path_parts.index(last_app_id_part)
            extra = original_path_parts[last_part_position+1:]
            request.path = "/v2/apps{app_id}/{extra}".format(app_id=app_id.rstrip("/"), extra="/".join(extra))
            request.path = request.path.rstrip("/")
        if original_path.startswith("/v2/groups"):
            extra = []
            group_id = modified_app_or_group.id or self.group_id
            group_id = group_id.rstrip("/")
            last_app_id_part = group_id.split("/")[-1]
            if last_app_id_part in original_path_parts:
                last_part_position = original_path_parts.index(last_app_id_part)
                extra = original_path_parts[last_part_position+1:]
            request.path = "/v2/groups{group_id}/{extra}".format(group_id=group_id.rstrip("/"), extra="/".join(extra))
            request.path = request.path.rstrip("/")

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
            if self.is_post():
                # Post em /v2/apps nao poder ser uma lista, tem que ser apenas uma app.
                apps_json_repr = apps_json_repr[0]
        elif self.is_delete():
            if self.is_group_request():
                group_id = self.group_id
                group_id_with_namespace = "/{}/{}".format(self.request.user.current_account.namespace, group_id.strip("/"))
                self.request.path = "/v2/groups{}".format(group_id_with_namespace)
            if self.is_app_request():
                group_id = self.app_id
                group_id_with_namespace = "/{}/{}".format(self.request.user.current_account.namespace, group_id.strip("/"))
                self.request.path = "/v2/apps{}".format(group_id_with_namespace)
            if self.is_queue_request():
                app_id = self.app_id
                app_id_with_namespace = "/{}/{}".format(self.request.user.current_account.namespace, app_id.strip("/"))
                self.request.path = "/v2/queue{}/delay".format(app_id_with_namespace)

            return self.request
        else:
            request_app, original_app = apps[0]
            self._adjust_request_path_if_needed(request, original_app)
            apps_json_repr = request_app.json_repr(minimal=True)

        request.data = json.dumps(apps_json_repr, cls=self.json_encoder)
        return request
