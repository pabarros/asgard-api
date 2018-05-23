
import os
from hollowman.marathonapp import AsgardApp

NET_BRIDGE = "BRIDGE"

class TransformJSONFilter:
    name = "transfomrjson"

    def write(self, user, request_app, original_app):
        if self._is_new_format(request_app) and self._is_env_enabled():
            return self._transform_to_old_format(request_app)
        return request_app

    def response(self, user, response_app, original_app):
        if self._is_old_format(response_app) and self._is_env_enabled():
            return self._transform_to_new_format(response_app)
        return response_app

    def _is_old_format(self, app: AsgardApp):
        return not self._is_new_format(app)

    def _is_new_format(self, app: AsgardApp):
        return app.networks or hasattr(app.container, "port_mappings")

    def _transform_to_new_format(self, app: AsgardApp):
        if app.container.docker.network.lower() == NET_BRIDGE.lower():
            app.networks = [{"mode": "container/bridge"}]
        else:
            app.networks = [{"mode": "host"}]

        del app.container.docker.network
        app.container.port_mappings = app.container.docker.port_mappings
        return app

    def _transform_to_old_format(self, app: AsgardApp):
        if app.networks[0]['mode'] == "container/bridge":
            app.container.docker.network = "BRIDGE"
        else:
            app.container.docker.network = "HOST"

        del app.networks
        app.container.docker.port_mappings = app.container.port_mappings
        del app.container.port_mappings
        return app

    def _is_env_enabled(self):
        return os.getenv("ASGARD_FILTER_TRANSFORMJSON_ENABLED", "0") == "1"
