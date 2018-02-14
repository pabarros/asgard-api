from hollowman.marathonapp import AsgardMarathonApp


class AddAppNameFilter:

    name = 'appname'

    def write(self, user, request_app, original_app):
        if not hasattr(request_app.container, "docker"):
            return request_app

        appname = "hollowman.appname={}".format(original_app.id)
        params = request_app.container.docker.parameters

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

