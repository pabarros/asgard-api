
from hollowman.marathonapp import AsgardApp

class TransformJSONFilter:
    name = "transfomrjson"

    def write(self, user, request_app, original_app):
        pass

    def response(self, user, response_app, original_app):
        pass

    def _is_new_format(self, app: AsgardApp):
        return app.networks or hasattr(app.container, "port_mappings")
