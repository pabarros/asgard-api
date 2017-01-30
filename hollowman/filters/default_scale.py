#encoding: utf-8

import json
from marathon import MarathonClient
from hollowman.filters import BaseFilter


class DefaultScaleRequestFilter(BaseFilter):

    def __init__(self, ctx):
        super(DefaultScaleRequestFilter, self).__init__(ctx)

    def run(self, request):
        if request.is_json and request.data:
            data = json.loads(request.data)
            if request.method in ['PUT','POST'] and self.is_single_app(data):
                current_app_scale = self.get_current_scale(self.get_app_id(request.path))
                if 'instances' in data and data['instances'] == 0 and current_app_scale != 0:
                    if 'labels' not in data:
                        data['labels'] = {}
                    data['labels'].update({
                        'hollowman.default_scale': str(current_app_scale)
                    })

            request.data = json.dumps(data)

        return request

    def get_current_scale(self, app_id):
        return self.ctx.marathon_client.get_app(app_id).instances
