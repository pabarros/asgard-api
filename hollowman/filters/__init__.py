#encoding: utf-8

from marathon.models.app import MarathonApp

class BaseFilter(object):

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
        return "v2/apps" in request_path and self.get_app_id(request_path)

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
        return '/'.join(split_).replace('v2/apps', '')

    def get_original_app(self, ctx):
        """
        :rtype: marathon.models.app.MarathonApp
        """
        try:
            return ctx.marathon_client.get_app(self.get_app_id(ctx.request.path))
        except Exception as e:
            # TODO: Logar que tivemos essa exception
            return MarathonApp()

    def is_app_network_host(self, app):
        return hasattr(app.container, "docker") and app.container.docker.network == 'HOST'


class Context(object):

    def __init__(self, marathon_client, request):
        self.marathon_client = marathon_client
        self.request = request
