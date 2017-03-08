#encoding: utf-8
import json
from hollowman.filters import BaseFilter


class DNSRequestFilter(BaseFilter):

    def run(self, ctx):
        request = ctx.request
        if request.is_json and request.data:
            body = json.loads(request.data)

            if self.is_request_on_app(request.path) and self._payloas_has_only_env(request, body):
                # Só temos as envs nesse payload, vamos buscar a app original e mesclar com o payload
                original_app = self.get_original_app(ctx)
                if not original_app.env:
                    original_app.env = {}
                for key, value in body['env'].iteritems():
                    original_app.env[key] = value
                body = json.loads(original_app.to_json())

            if self.is_single_app(body):
                body = self.patch_app_dns_parameters(body)
            if self.is_multi_app(body):
                for app in body:
                    self.patch_app_dns_parameters(app)
            if self.is_group(body):
                self.patch_apps_from_group(body)

            request.data = json.dumps(body)
        return request

    def _payloas_has_only_env(self, request, body):
        return  request.method == "PUT" and ('env' in body and len(body.keys()) == 1)

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
