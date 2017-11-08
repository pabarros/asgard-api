from marathon.models import MarathonDeployment

from hollowman.marathonapp import SieveMarathonApp


class NameSpaceFilter:
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
            request_app.id = self._add_namespace(
                app_id=request_app.id,
                namespace=user.current_account.namespace
            )
            return request_app

        request_app.id = self._add_namespace(
            app_id=request_app.id,
            namespace=user.current_account.namespace
        )

        return request_app

    def _add_namespace(self, app_id: str, namespace: str) -> str:
        namespace_part = "/{namespace}".format(namespace=namespace)
        appname_part = app_id.strip("/")

        return f"{namespace_part}/{appname_part}"

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

    def response_deployment(self, user, deployment: MarathonDeployment) -> MarathonDeployment:
        deployment.affected_apps = [
            self._add_namespace(app_id, user.current_account.namespace)
            for app_id in deployment.affected_apps
        ]

        for action in deployment.current_actions:
            action.app = self._add_namespace(action.app,
                                             user.current_account.namespace)

        for step in deployment.steps:
            for action in step.actions:
                action.app = self._add_namespace(action.app,
                                                 user.current_account.namespace)

        return deployment
