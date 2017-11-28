

class AddURIFilter:

    name = "uri"
    DOCKER_AUTH_URI =  "file:///etc/docker.tar.bz2"

    def write(self, user, request_app, original_app):
        if self.DOCKER_AUTH_URI not in request_app.uris:
            request_app.uris.append(self.DOCKER_AUTH_URI)
        return request_app
