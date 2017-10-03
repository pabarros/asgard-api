
import json

from hollowman.filters import BaseFilter


class AddAppNameFilter(BaseFilter):

    name = 'appname'

    def write(self, user, request_app, original_app):
        appname = "hollowman.appname={}".format(request_app.id)
        try:
            params = request_app.container.docker.parameters
        except AttributeError:
            params = []

        for p in params:
            if p['key'] == "label" and p['value'].startswith("hollowman.appname"):
                p['value'] = appname
                break
        else:
            params.append({
                "key": "label",
                "value": appname
            })


        return request_app
