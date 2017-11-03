
from flask import request

from hollowman.marathonapp import SieveMarathonApp



class NameSpaceFilter():
    name = "namespace"

    def _remove_namespace(self, user, id_):
        id_without_ns = id_.replace("/{}".format(user.current_account.namespace), "")
        if not id_without_ns:
            id_without_ns = "/"
        return id_without_ns

    def write(self, user, request_app, original_app):

        if not user:
            return request_app

        if not original_app.id:
            self._add_namespace_to_appid(request_app, user.current_account.namespace)
            return request_app

        self._add_namespace_to_appid(request_app, user.current_account.namespace)

        return request_app

    def _add_namespace_to_appid(self, request_app, namespace):
        namespace_part = "/{namespace}".format(namespace=namespace)
        appname_part = request_app.id.strip("/")
        request_app.id = "/".join([namespace_part, appname_part])

    def _remove_namespace_from_tasks(self, task_list, namespace):
        for task in task_list:
            task.id = task.id.replace("{}_".format(namespace), "")
            task.app_id = task.app_id.replace("/{}/".format(namespace), "/")

    def response(self, user, response_app, original_app) -> SieveMarathonApp:
        if not user:
            return response_app

        response_app.id = response_app.id.replace("/{}/".format(user.current_account.namespace), "/")
        self._remove_namespace_from_tasks(response_app.tasks, user.current_account.namespace)

        return response_app

    def response_group(self, user, response_group, original_group):
        response_group.id = self._remove_namespace(user, response_group.id)
        for app in response_group.apps:
            app.id = self._remove_namespace(user, app.id)
            self._remove_namespace_from_tasks(app.tasks, user.current_account.namespace)

        return response_group

