import json
from typing import Dict

from marathon import MarathonApp

from hollowman.filters import BaseFilter


class TrimRequestFilter(BaseFilter):
    name = 'trim'
    app_attrs_to_trim = ('labels', 'env')

    def run(self, ctx):
        request = ctx.request
        if request.is_json and request.data:
            data = json.loads(request.data)
            _new_envs = {}
            _new_labels = {}
            if 'env' in data:
                for key, value in data['env'].items():
                    _new_envs[key.strip()] = value.strip()
                data['env'] = _new_envs

            if 'labels' in data:
                for key, value in data['labels'].items():
                    _new_labels[key.strip()] = value.strip()
                data['labels'] = _new_labels

            request.data = json.dumps(data)
        return request

    def _trim_dict_items(self, d: Dict[str, str]) -> Dict[str, str]:
        new = {}
        for k, v in d.items():
            new[k.strip()] = v.strip()
        return new

    def write(self, user, request_app: MarathonApp, app: MarathonApp) -> MarathonApp:
        for name in self.app_attrs_to_trim:
            attr = getattr(request_app, name)
            if attr:
                setattr(request_app, name, self._trim_dict_items(attr))
        return request_app
