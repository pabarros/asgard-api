#encoding: utf-8

import json
from hollowman.filters import BaseFilter

class ForcePullFilter(BaseFilter):

    def __init__(self, ctx):
        super(ForcePullFilter, self).__init__(ctx)

    def run(self, request):
        data = request.get_json()

        if self.is_single_app(data):
            if 'labels' in data and ('hollowman.disable_forcepull' in data['labels']):
                value = False
            else:
                value = True

            data.update({
                "container": {
                    "docker": {
                        "forcePullImage": value
                    }
                }
            })

            request.data = json.dumps(data)

        return request
