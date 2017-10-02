#encoding: utf-8

import json

from hollowman.filters import BaseFilter


class ForcePullFilter(BaseFilter):

    name = 'pull'

    def run(self, ctx):
        request = ctx.request
        if request.is_json and request.data:
            data = request.get_json()

            if self.is_single_app(data):
                original_app_dict = json.loads(self.get_original_app(ctx).to_json())
                original_app_dict.update(data)

                if self.is_docker_app(original_app_dict):
                    original_app_dict['container']['docker']["forcePullImage"] = True

                request.data = json.dumps(original_app_dict)

        return request

    def write(sef, user, request_app, app):
        if request_app.container and request_app.container.docker:
            request_app.container.docker.force_pull_image = True
        return request_app

