import abc
from typing import Tuple, List

from marathon import MarathonApp
from marathon.util import MarathonMinimalJsonEncoder

from hollowman import conf
from hollowman.hollowman_flask import OperationType
from hollowman.marathonapp import SieveMarathonApp


Apps = List[Tuple[SieveMarathonApp, MarathonApp]]


class HTTPWrapper(metaclass=abc.ABCMeta):
    json_encoder = MarathonMinimalJsonEncoder
    marathon_client = conf.marathon_client

    app_path_prefix = '/v2/apps'
    group_path_prefix = '/v2/groups'

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
