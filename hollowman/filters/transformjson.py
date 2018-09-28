
from flask import request

import os
from hollowman.marathonapp import AsgardApp

NET_BRIDGE = "BRIDGE"

class TransformJSONFilter:
    """
    Esse filtro só vai existir até o momento em que atualizarmos para o Marathon 1.5.x;
    Enquanto estivermos no 1.3.x ou 1.4.x precisamos desse filtro pois nossa UI já está na
    versão nova (que já usa o formato do backend 1.5.x).
    Esse filtro faz a camada de compatibilidade entre a UI nova e o backend velho.
    Se eventualmente voltarmos a usar UI velha, esse filtro detecta isso e não faz nada.
    """
    name = "transfomrjson"

    def write(self, user, request_app, original_app):
        if self._is_new_format(request_app) and self._is_new_ui():
            return self._transform_to_old_format(request_app)
        return request_app

    def response(self, user, response_app, original_app):
        if self._is_old_format(response_app) and self._is_new_ui():
            return self._transform_to_new_format(response_app)
        return response_app

    def _is_old_format(self, app: AsgardApp):
        return not self._is_new_format(app)

    def _is_new_format(self, app: AsgardApp):
        return app.networks or hasattr(app.container, "port_mappings")

    def _transform_to_new_format(self, app: AsgardApp):
        network_attr = getattr(app.container.docker, 'network', NET_BRIDGE.lower())
        if network_attr.lower() == NET_BRIDGE.lower():
            app.networks = [{"mode": "container/bridge"}]
        else:
            app.networks = [{"mode": "host"}]

        if hasattr(app.container.docker, 'network'):
            del app.container.docker.network

        if hasattr(app.container.docker, 'port_mappings') and app.container.docker.port_mappings:
            app.container.port_mappings = app.container.docker.port_mappings
        return app

    def _transform_to_old_format(self, app: AsgardApp):
        if app.networks[0]['mode'] == "container/bridge":
            app.container.docker.network = "BRIDGE"
        else:
            app.container.docker.network = "HOST"

        del app.networks

        app.container.docker.port_mappings = getattr(app.container, "port_mappings", None)
        try:
            del app.container.port_mappings
        except Exception as e:
            pass

        return app

    def _is_new_ui(self):
        """
        Detecta se quem está fazendo o request é a UI nova.
        """
        return request.headers.get("X-UI-Version", None)
