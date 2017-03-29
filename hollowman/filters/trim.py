#encoding: utf-8

import json
from hollowman.filters import BaseFilter

class TrimRequestFilter(BaseFilter):

    name = 'trim'

    def run(self, ctx):
        request = ctx.request
        if request.is_json and request.data:
            data = json.loads(request.data)
            _new_envs = {}
            _new_labels = {}
            if 'env' in data:
                for key, value in data['env'].iteritems():
                    _new_envs[key.strip()] = value.strip()
                data['env'] = _new_envs

            if 'labels' in data:
                for key, value in data['labels'].iteritems():
                    _new_labels[key.strip()] = value.strip()
                data['labels'] = _new_labels

            request.data = json.dumps(data)
        return request
