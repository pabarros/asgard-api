import json
from flask import Response as FlaskResponse

from marathon.models.group import MarathonGroup

from hollowman.http_wrappers.base import HTTPWrapper, Apps
from hollowman.marathonapp import SieveMarathonApp
from hollowman.marathon.group import SieveAppGroup


class Response(HTTPWrapper):
    def __init__(self, request, response: FlaskResponse):
        self.request = request
        self.response = response

    def is_deployment_id_response(self):
        pass

    def _remove_namespace_if_exists(self, namespace, group_id):
        if group_id is not None:
            return group_id.replace("/{}".format(namespace), "", 1)

    def split(self) -> Apps:

        if self.is_read_request():
            response_content = json.loads(self.response.data)
            if self.is_list_apps_request():
                for app in response_content['apps']:
                    response_app = SieveMarathonApp.from_json(app)
                    app = self.marathon_client.get_app(self.app_id or response_app.id)
                    yield response_app, app
                return
            elif self.is_group_request():
                response_group = SieveAppGroup(MarathonGroup().from_json(response_content))
                for current_group in response_group.iterate_groups():
                    group_id = current_group.id
                    group_id_without_namespace = self._remove_namespace_if_exists(self.request.user.current_account.namespace, group_id)
                    original_group = self._get_original_group(self.request.user, group_id_without_namespace)
                    yield current_group, original_group
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
