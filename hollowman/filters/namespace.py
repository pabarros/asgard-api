from marathon.models import MarathonDeployment
from marathon.models.task import MarathonTask

from hollowman.marathonapp import AsgardApp


class NameSpaceFilter:
    name = "namespace"

    def _remove_namespace(self, id_, namespace):
        id_without_ns = id_.replace("/{}".format(namespace), "", 1)
        if not id_without_ns:
            id_without_ns = "/"
        return id_without_ns

    def write_task(self, user, request_task, original_task):
        try:
            request_task.app_id = self._add_namespace(
                app_id=request_task.app_id,
                namespace=user.current_account.namespace
            )
        except AttributeError as e:
            pass
        request_task.id = "{namespace}_{task_id}".format(namespace=user.current_account.namespace, task_id=request_task.id)
        return request_task

    def write(self, user, request_app, original_app):

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
            task.id = task.id.replace("{}_".format(namespace), "", 1)
            task.app_id = self._remove_namespace(task.app_id, namespace)

    def response(self, user, response_app, original_app) -> AsgardApp:
        if not response_app.id.startswith("/{}/".format(user.current_account.namespace)):
             return None

        response_app.id = self._remove_namespace(response_app.id, user.current_account.namespace)
        self._remove_namespace_from_tasks(response_app.tasks, user.current_account.namespace)

        return response_app

    def response_group(self, user, response_group, original_group):
        response_group.id = self._remove_namespace(response_group.id, user.current_account.namespace)
        for app in response_group.apps:
            app.id = self._remove_namespace(app.id, user.current_account.namespace)
            self._remove_namespace_from_tasks(app.tasks, user.current_account.namespace)

        return response_group

    def response_deployment(self, user, deployment: MarathonDeployment, original_deployment) -> MarathonDeployment:
        # Não teremos deployments que afetam apps de múltiplos namespaces,
        # por isos podemos olhar apenas umas das apps.
        original_affected_apps_id = deployment.affected_apps[0]
        deployment.affected_apps = [
            self._remove_namespace(app_id, user.current_account.namespace)
            for app_id in deployment.affected_apps
        ]

        for action in deployment.current_actions:
            action.app = self._remove_namespace(action.app, user.current_account.namespace)

        for step in deployment.steps:
            for action in step.actions:
                action.app = self._remove_namespace(action.app, user.current_account.namespace)

        if original_affected_apps_id.startswith(f"/{user.current_account.namespace}/"):
            return deployment
        return None

    def response_queue(self, user, response_queue, original_queue):
        current_namespace = user.current_account.namespace
        if response_queue.app.id.startswith("/{}/".format(current_namespace)):
            response_queue.app.id = self._remove_namespace(response_queue.app.id, user.current_account.namespace)
            return response_queue
        return None

    def response_task(self, user, response_task, original_task):
        """
        Método para filtrar tasks que estejam sendo retornadas no
        response

        :response_task: Task que está presende no response
        :original_task: Task original, por enquanto é o mesmo objeto do response_task
        :returns: response_task modificado

        """
        if response_task.id.startswith(f"{user.current_account.namespace}_"):
            self._remove_namespace_from_tasks([response_task], user.current_account.namespace)
            return response_task
        return None

