class LabelsFilter:
    def write(self, user, request_app, original_app):
        request_app.labels.pop("traefik.backend", None)
        return request_app
