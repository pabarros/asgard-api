# encoding: utf-8

import json

from hollowman.log import logger


class ForcePullFilter:

    name = "pull"

    def write(sef, user, request_app, app):
        try:
            request_app.container.docker.force_pull_image = True
            logger.info("Forcing pull image of app {}".format(request_app.id))
        except AttributeError as e:
            pass
        return request_app
