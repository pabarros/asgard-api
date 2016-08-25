from flask import Flask, url_for, redirect, Response, request

from hollowman.conf import MARATHON_ENDPOINT
from hollowman.upstream import replay_request

application = Flask(__name__)


@application.route("/", methods=["GET"])
def index():
    return Response(status=301, headers={"Location": url_for("ui")})

@application.route('/ui', defaults={'path': '/'})
@application.route('/ui/', defaults={'path': ''})
@application.route('/ui/<path:path>')
def ui(path):
    r = replay_request(request, MARATHON_ENDPOINT)
    h = dict(r.headers)
    h.pop("Transfer-Encoding", None)
    return Response(response=r.content, status=r.status_code, headers=h)

@application.route('/v2', defaults={'path': '/'})
@application.route('/v2/', defaults={'path': ''})
@application.route('/v2/<path:path>', methods=["GET", "POST", "PUT", "DELETE"])
def apiv2(path):
    r = replay_request(request, MARATHON_ENDPOINT)
    h = dict(r.headers)
    h.pop("Transfer-Encoding", None)
    return Response(response=r.content, status=r.status_code, headers=h)

