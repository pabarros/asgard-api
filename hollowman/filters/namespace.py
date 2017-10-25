from hollowman.marathonapp import SieveMarathonApp


class NameSpaceFilter():
    name = "namespace"

    def write(self, user, request_app, original_app):

        if not user:
            return request_app

        if not original_app.id:
            self._add_namespace_to_appid(request_app, user.current_account.namespace)
            return request_app

        original_app_current_namespace = original_app.id.strip("/").split("/")[0]

        if (user.current_account.namespace == original_app_current_namespace):
            self._add_namespace_to_appid(request_app, user.current_account.namespace)

        return request_app

    def _add_namespace_to_appid(self, request_app, namespace):
        namespace_part = "/{namespace}".format(namespace=namespace)
        appname_part = request_app.id.strip("/")
        request_app.id = "/".join([namespace_part, appname_part])

    def response(self, user, response_app, original_app) -> SieveMarathonApp:
        if not user:
            return response_app

        original_app_current_namespace = original_app.id.strip("/").split("/")[0]
        if (user.current_account.namespace == original_app_current_namespace):
            response_app.id = response_app.id.replace("/{}/".format(user.current_account.namespace), "/")

        return response_app
