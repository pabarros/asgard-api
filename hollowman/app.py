#encoding: utf-8

from datetime import timedelta

from flask import request
from flask_cors import CORS

from hollowman.hollowman_flask import HollowmanFlask
from hollowman.conf import SECRET_KEY, CORS_WHITELIST
from hollowman.log import logger

application = HollowmanFlask(__name__)
application.secret_key = SECRET_KEY
application.permanent_session_lifetime = timedelta(minutes=5)
application.config["JWT_AUTH_URL_RULE"] = None
application.config["JWT_EXPIRATION_DELTA"] = timedelta(days=1)

CORS(application, origins=CORS_WHITELIST)

@application.after_request
def after_request(response):
    logger.info(
        {
            "method": request.method,
            "status_code": response.status_code,
            "path": request.path,
            "user": (hasattr(request, "user") and request.user) or None,
            "location": response.headers.get("Location"),
            "qstring": request.args
        }
    )
    return response

import hollowman.routes

