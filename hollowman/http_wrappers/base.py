import abc

from marathon.util import MarathonMinimalJsonEncoder


class HTTPWrapper(metaclass=abc.ABCMeta):
    json_encoder = MarathonMinimalJsonEncoder

    app_path_prefix = '/v2/apps'
    group_path_prefix = '/v2/groups'