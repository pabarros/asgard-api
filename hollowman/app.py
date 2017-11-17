#encoding: utf-8

from datetime import timedelta
import json
import traceback
import sys

from flask import request, Blueprint, Response
from flask_cors import CORS

from hollowman.hollowman_flask import HollowmanFlask
from hollowman.conf import SECRET_KEY, CORS_WHITELIST
from hollowman.log import logger
from hollowman.plugins import register_plugin
from hollowman.auth.jwt import jwt_auth

from hollowman.metrics.zk.routes import zk_metrics_blueprint
from hollowman.api.account import account_blueprint

application = HollowmanFlask(__name__)
application.url_map.strict_slashes = False
application.secret_key = SECRET_KEY
application.permanent_session_lifetime = timedelta(minutes=5)
application.config["JWT_AUTH_URL_RULE"] = None
application.config["JWT_EXPIRATION_DELTA"] = timedelta(days=7)

application.register_blueprint(zk_metrics_blueprint, url_prefix="/_cat/metrics/zk")
application.register_blueprint(account_blueprint, url_prefix="/hollow/account")

CORS(application, origins=CORS_WHITELIST)
jwt_auth.init_app(application)


def _get_current_exception_if_exists(current_request):
    try:
        return current_request.current_exception
    except Exception as e:
        return None

@application.after_request
def after_request(response):
    logger.info(
        {
            "method": request.method,
            "status_code": response.status_code,
            "path": request.path,
            "user": (hasattr(request, "user") and request.user.tx_email) or None,
            "account_id": (hasattr(request, "user") and request.user.current_account.id) or None,
            "location": response.headers.get("Location"),
            "qstring": request.args,
            "error": _get_current_exception_if_exists(request)
        }
    )
    return response

@application.errorhandler(Exception)
def handler_500(error):
    current_exception = {
        "message": str(error),
        "traceback": traceback.format_exc(),
        "type": sys.exc_info()[0].__name__,
    }
    request.current_exception = current_exception

    return Response(
        response=json.dumps(current_exception),
        status=500
    )

import marathon
marathon.log = logger

import hollowman.routes
register_plugin("example-plugin")
register_plugin("session-checker-plugin")

