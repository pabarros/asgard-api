#encoding: utf-8

import json
from marathon import MarathonClient

class DefaultScaleRequestFilter(object):
    def run(self, request):
        data = request.get_json()

        #make sure we are using the "suspend button"
        if 'instances' in data and data['instances'] == 0 and len(data) == 1:
            data['labels'].merge({
                'default_scale': self.get_last_scale(get_app_id(request))
            })

    def get_app_id(self, request):
        return '/' + url.split('//')[2]

    def get_last_scale(self, app_id):
        return 1
