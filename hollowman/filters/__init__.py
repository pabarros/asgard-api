#encoding: utf-8


class BaseFilter(object):

    def __init__(self, ctx):
        self.ctx = ctx

    def is_single_app(self, body):
        has_groups = 'groups' in body
        has_apps = 'apps' in body
        is_dict = isinstance(body, dict)
        return is_dict and not has_groups and not has_apps

    def is_multi_app(self, body):
        is_list = isinstance(body, list)
        return is_list and not self.is_single_app(body)

    def is_docker_app(self, body):
        has_container = 'container' in body
        has_docker = has_container and ('docker' in body['container'])
        return has_docker

    def is_request_on_app(self, request_path):
        """
        Verifica se o path corresponde a uma app específica
        ex: /v2/apps/<app-id> retorna True
        /v2/grups deve retornar False
        """
        remain = request_path.replace("/v2/apps/", "")
        return "v2/apps" in request_path\
                and len(remain) > 0\
                and request_path != "/v2/apps"

    def is_group(self, body):
        has_groups = 'groups' in body
        has_apps = 'apps' in body
        return has_groups or has_apps

    def get_apps_from_group(self, group):
        if 'apps' in group:
            return group['apps']
        return []

    def get_app_id(self, request_path):
        split_ = request_path.split('/')
        cut_limit = len(split_)
        api_paths = [
            'restart',
            'tasks',
            'versions',
        ]
        if any([path in request_path for path in api_paths]):
            locations = [split_.index(path) for path in api_paths if path in split_]
            cut_limit = min(locations)
        return '/'.join(split_[:cut_limit]).replace('/v2/apps/', '')


class Context(object):

    def __init__(self, marathon_client):
        self.marathon_client = marathon_client
