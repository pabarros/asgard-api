#encoding: utf-8

import json

class TrimRequestFilter(object):
    def run(self, request):
        data = request.get_json()
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
