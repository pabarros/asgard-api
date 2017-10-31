import abc
from typing import Tuple, List

from marathon import MarathonApp, NotFoundError
from marathon.util import MarathonJsonEncoder

from hollowman import conf
from hollowman.hollowman_flask import OperationType
from hollowman.marathonapp import SieveMarathonApp
from hollowman.marathon.group import SieveAppGroup


Apps = List[Tuple[SieveMarathonApp, MarathonApp]]


class HTTPWrapper(metaclass=abc.ABCMeta):
    json_encoder = MarathonJsonEncoder
    marathon_client = conf.marathon_client

    app_path_prefix = '/v2/apps'
    group_path_prefix = '/v2/groups'

    def is_delete(self):
        return self.request.method == "DELETE"

    def is_post(self):
        return self.request.method == "POST"

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

    @property
    def group_id(self) -> str:
        reserved_paths = [
            "versions",
        ]
        return self._get_object_id(reserved_paths, "v2/groups")

    @property
    def app_id(self) -> str:
        """
        self.request.path = '/v2/apps//marathon/app/id' -> '//marathon/app/id'
        self.request.path = '/v2/apps/marathon/app/id' -> '/marathon/app/id'


        Marathon's api accept both double or single slashes at the beginning

        """
        reserved_paths = [
            'restart',
            'tasks',
            'versions',
        ]
        return self._get_object_id(reserved_paths, "v2/apps")

    def _get_original_app(self, user, app_id):
        try:
            if not user:
                return self.marathon_client.get_app(app_id)

            app_id_with_namespace = "/{}/{}".format(user.current_account.namespace,
                                                    app_id.strip("/"))
            try:
                return self.marathon_client.get_app(app_id_with_namespace)
            except NotFoundError as e:
                return self.marathon_client.get_app(app_id)
        except NotFoundError:
            return MarathonApp()

    def _get_original_group(self, user, group_id):
        try:

            group_id_with_namespace = "/{}/{}".format(user.current_account.namespace,
                                                    (group_id or "/").strip("/"))
            try:
                return SieveAppGroup(self.marathon_client.get_group(group_id_with_namespace))
            except NotFoundError as e:
                return SieveAppGroup(self.marathon_client.get_group(group_id))
        except NotFoundError:
            return SieveAppGroup()
