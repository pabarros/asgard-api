import json
from typing import Dict

from hollowman.marathonapp import AsgardMarathonApp


class TrimRequestFilter():
    name = 'trim'
    app_attrs_to_trim = ('labels', 'env')

    def _trim_dict_items(self, d: Dict[str, str]) -> Dict[str, str]:
        new = {}
        for k, v in d.items():
            new[k.strip()] = v.strip()
        return new

    def write(self, user, request_app: AsgardMarathonApp, app: AsgardMarathonApp) -> AsgardMarathonApp:
        for name in self.app_attrs_to_trim:
            attr = getattr(request_app, name)
            setattr(request_app, name, self._trim_dict_items(attr))
        return request_app
