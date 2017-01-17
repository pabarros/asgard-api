#encoding: utf-8

import json

class TrimEnvVarsRequestFilter(object):
    def run(self, request):
        data = request.get_json()
        if 'env' in data:
            for key, value in data['env'].iteritems():
                data['env'][key] = value.strip()
            request.data = json.dumps(data)
        return request
