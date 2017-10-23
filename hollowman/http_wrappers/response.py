import json
from flask import Response as FlaskResponse
from hollowman.http_wrappers.base import HTTPWrapper, Apps
from hollowman.marathonapp import SieveMarathonApp


class Response(HTTPWrapper):
    def __init__(self, request, response: FlaskResponse):
        self.request = request
        self.response = response

    def is_deployment_id_response(self):
        pass


    def split(self) -> Apps:
        if self.is_group_request():
            raise NotImplementedError()

        if self.is_read_request():
            response_content = json.loads(self.response.data)
            if self.is_list_apps_request():
                for app in response_content['apps']:
                    response_app = SieveMarathonApp.from_json(app)
                    app = self.marathon_client.get_app(self.app_id or response_app.id)
                    yield response_app, app
                return
            else:
                response_app = SieveMarathonApp.from_json(response_content['app'])
                app = self.marathon_client.get_app(self.app_id)
                yield response_app, app
                return

        yield SieveMarathonApp(), self.marathon_client.get_app(self.app_id)

    def join(self, apps: Apps) -> FlaskResponse:
        if self.is_group_request():
            raise NotImplementedError()

        if self.is_list_apps_request():
            apps_json_repr = [response_app.json_repr(minimal=True)
                              for response_app, _ in apps]
            body = {'apps': apps_json_repr}
        elif self.is_read_request() and self.is_app_request():
            # TODO: Retornar 404 nesse caso. Pensar em como fazer.
            # No caso de ser um acesso a uma app específica, e ainda sim recebermos apps = [],
            # deveríamos retornar 404. Chegar uma lista vazia qui significa que a app foi removida
            # do response, ou seja, quem fez o request não pode visualizar esses dados, portanto, 404.
            response_app = apps[0][0] if apps else SieveMarathonApp()
            body = {'app': response_app.json_repr(minimal=True)}

        return FlaskResponse(
            response=json.dumps(body, cls=self.json_encoder),
            status=self.response.status,
            headers=self.response.headers
        )
