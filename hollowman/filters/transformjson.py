
from hollowman.marathonapp import AsgardApp

NET_BRIDGE = "BRIDGE"

class TransformJSONFilter:
    name = "transfomrjson"

    def write(self, user, request_app, original_app):
        return self._transform_to_new_format(request_app)

    def response(self, user, response_app, original_app):
        return self._transform_to_new_format(response_app)

    def _is_new_format(self, app: AsgardApp):
        return app.networks or hasattr(app.container, "port_mappings")

    def _transform_to_new_format(self, app: AsgardApp):
        if app.container.docker.network.lower() == NET_BRIDGE.lower():
            app.networks = [{"name": "container/bridge"}]
            del app.container.docker.network
        app.container.port_mappings = app.container.docker.port_mappings
        return app

