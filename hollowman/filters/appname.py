

import json
from hollowman.filters import BaseFilter


class AddAppNameFilter(BaseFilter):

    name = 'appname'

    def run(self, ctx):
        request = ctx.request
        if request.is_json and request.data and self.is_request_on_app(request.path):
            data = request.get_json()
            original_app_dict = json.loads(self.get_original_app(ctx).to_json())
            original_app_dict.update(data)

            if 'parameters' not in original_app_dict['container']['docker']:
                original_app_dict['container']['docker']['parameters'] = []

            param_value = "hollowman.appname={}".format(original_app_dict['id'])
            self.patch_label_param(original_app_dict['container']['docker']['parameters'],
                                   key="label",
                                   value=param_value
            )

            request.data = json.dumps(original_app_dict)


        return request

    def patch_label_param(self, docker_params, key, value):
        found = False
        for param in docker_params:
            if param['key'] == "label" and param['value'].startswith("hollowman.appname="):
                param['value'] = value
                found = True

        if not found:
            docker_params.append(
                {
                    "key": key,
                    "value": value
                }
            )
