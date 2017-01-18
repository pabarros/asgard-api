class BaseFilter(object):

    def is_single_app(self, request):
        data = request.get_json()
        has_groups = 'groups' in data
        has_apps = 'apps' in data
        is_dict = isinstance(data, dict)
        return is_dict and not has_groups and not has_apps

    def is_multi_app(self, request):
        data = request.get_json()
        is_list = isinstance(data, list)
        return is_list and not self.is_single_app(data)

    def is_docker_app(self, request):
        data = request.get_json()
        has_container = 'container' in data
        has_docker = has_container and ('docker' in data['container'])
        return has_docker

    def is_group(self, request):
        data = request.get_json()
        has_groups = 'groups' in data
        has_apps = 'apps' in data
        return has_groups or has_apps

    def get_apps_from_group(self, group):
        if 'apps' in group:
            return group['apps']
        return []

    def get_app_id(self, request_path):
        return '/' + request_path.split('//')[-1]
