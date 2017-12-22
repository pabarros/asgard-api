import abc
from typing import Tuple, List
from werkzeug.utils import cached_property
from enum import Enum, auto

from marathon import MarathonApp, NotFoundError
from marathon.util import MarathonJsonEncoder
from marathon.models.group import MarathonGroup

from hollowman import conf
from hollowman.hollowman_flask import OperationType
from hollowman.marathonapp import SieveMarathonApp
from hollowman.marathon.group import SieveAppGroup


Apps = List[Tuple[SieveMarathonApp, MarathonApp]]


class RequestResource(Enum):
    APPS = auto()
    GROUPS = auto()
    DEPLOYMENTS = auto()

class HTTPWrapper(metaclass=abc.ABCMeta):
    json_encoder = MarathonJsonEncoder
    marathon_client = conf.marathon_client

    app_path_prefix = '/v2/apps'
    group_path_prefix = '/v2/groups'
    deployment_prefix = '/v2/deployments'
    tasks_prefix = '/v2/tasks'
    queue_prefix = '/v2/queue'

    API_RESERVED_PATHS_PER_ENDPOINT = {
        "apps": ['restart', 'tasks', 'versions'],
        "groups": ["versions"],
        "deployments": [],
        "tasks": [],
        "queue": ["delay"],
    }

    def is_delete(self):
        return self.request.method == "DELETE"

    def is_post(self):
        return self.request.method == "POST"

    def is_write_request(self) -> bool:
        return OperationType.WRITE in self.request.operations

    def is_read_request(self) -> bool:
        return OperationType.READ in self.request.operations

    def is_tasks_request(self):
        """
        It's a request at /v2/tasks/* ?
        """
        return self.request.path.startswith(self.tasks_prefix)

    def is_app_request(self):
        """
        It's a request at /v2/apps/* ?
        """
        return self.request.path.startswith(self.app_path_prefix)

    def is_list_apps_request(self):
        """
        It's a request at /v2/apps/$ ?
        """
        return self.is_app_request() and self.object_id is None

    def is_group_request(self):
        """
        It's a request at /v2/groups/* ?
        """
        return self.request.path.startswith(self.group_path_prefix)

    def is_deployment(self) -> bool:
        return self.request.path.startswith(self.deployment_prefix)

    def is_queue_request(self) -> bool:
        return self.request.path.startswith(self.queue_prefix)

    def _get_object_id(self, reserved_paths, endpoint_prefix):
        split_ = self.request.path.split('/')
        api_paths = reserved_paths
        locations = [split_.index(path) for path in api_paths if path in split_]
        cut_limit = min(locations or [len(split_)])
        # Removes every path after the app name
        split_ = split_[:cut_limit]

        # Removes evey empty path
        split_ = [part for part in split_ if part]
        return '/'.join(split_).replace(endpoint_prefix, '') or None

    @cached_property
    def object_id(self) -> str:
        if self.is_tasks_request():
            return None
        base_path = [p for p in self.request.path.split("/") if p][:2]
        endpoint_name = base_path[1]
        return self._get_object_id(self.API_RESERVED_PATHS_PER_ENDPOINT.get(endpoint_name, []), "/".join(base_path))

    @cached_property
    def request_resource(self) -> RequestResource:
        if self.is_app_request():
            return RequestResource.APPS
        if self.is_group_request():
            return RequestResource.GROUPS
        if self.is_deployment():
            return RequestResource.DEPLOYMENTS

    def _get_original_app(self, user, app_id):
        if not user:
            return self.marathon_client.get_app(app_id)

        app_id_with_namespace = "/{}/{}".format(user.current_account.namespace,
                                                app_id.strip("/"))
        try:
            return self.marathon_client.get_app(app_id_with_namespace)
        except NotFoundError as e:
            return MarathonApp.from_json({"id": app_id_with_namespace})

    def _get_original_group(self, user, group_id):
        group_id_with_namespace = "/{}/{}".format(user.current_account.namespace,
                                                (group_id or "/").strip("/"))
        try:
            return SieveAppGroup(self.marathon_client.get_group(group_id_with_namespace))
        except NotFoundError as e:
            return SieveAppGroup(MarathonGroup.from_json({"id": group_id_with_namespace}))
