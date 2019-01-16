class DefaultScaleFilter:

    name = "defaultscale"

    def write(self, user, request_app, original_app):
        if original_app.instances and request_app.instances == 0:
            request_app.labels["hollowman.default_scale"] = str(
                original_app.instances
            )
        return request_app
