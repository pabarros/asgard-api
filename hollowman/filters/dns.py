import json
from hollowman.filters import BaseFilter


class DNSRequestFilter(BaseFilter):

    def run(self, request):
        if request.is_json and request.data:
            body = request.get_json()
            if self.is_single_app(body):
                body = self.patch_app_dns_parameters(body)
            if self.is_multi_app(body):
                for app in body:
                    self.patch_app_dns_parameters(app)
            if self.is_group(body):
                self.patch_apps_from_group(body)
            request.data = json.dumps(body)
        return request

    def patch_app_dns_parameters(self, data):
        if self.is_docker_app(data):
            if not 'parameters' in data['container']['docker']:
                data['container']['docker']['parameters'] = []

            params = dict((param['key'], param)for param in data['container']['docker']['parameters'])
            params['dns'] = {"key": "dns", "value": "172.17.0.1"}
            data['container']['docker']['parameters'] = params.values()
        return data

    def patch_apps_from_group(self, group):
        for app in self.get_apps_from_group(group):
            self.patch_app_dns_parameters(app)
        if 'groups' in group:
            for subgroup in group['groups']:
                self.patch_apps_from_group(subgroup)
