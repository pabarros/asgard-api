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
                    app = self.marathon_client.get_app(self.app_id)
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

        if self.is_read_request() and self.is_app_request():
            response_app, _ = apps[0]
            body = {'app': response_app.json_repr(minimal=True)}
        if self.is_list_apps_request():
            apps_json_repr = [response_app.json_repr(minimal=True)
                              for response_app, _ in apps]
            body = {'apps': apps_json_repr}

        return FlaskResponse(
            response=json.dumps(body, cls=self.json_encoder),
            status=self.response.status,
            headers=self.response.headers
        )
