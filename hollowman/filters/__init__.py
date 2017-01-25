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

    def is_group(self, body):
        has_groups = 'groups' in body
        has_apps = 'apps' in body
        return has_groups or has_apps

    def get_apps_from_group(self, group):
        if 'apps' in group:
            return group['apps']
        return []

    def get_app_id(self, request_path):
        return '/' + request_path.split('//')[-1]


class Context(object):

    def __init__(self, marathon_client):
        self.marathon_client = marathon_client
