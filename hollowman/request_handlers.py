from flask import Response

from hollowman.dispatcher import dispatch
from hollowman.parsers import RequestParser
from hollowman.hollowman_flask import HollowmanRequest
from hollowman import upstream, conf


def upstream_request(request: HollowmanRequest, run_filters=True) -> Response:
    resp = upstream.replay_request(request, conf.MARATHON_ENDPOINT)
    return Response(response=resp.content,
                    status=resp.status_code,
                    headers=dict(resp.headers))


def new(request: HollowmanRequest) -> Response:
    request_parser = RequestParser(request)

    if request_parser.is_group_request():
        return old(request)

    filtered_apps = []
    for request_app, app in request_parser.split():
        filtered_request_app = dispatch(operations=request.operations,
                                        user=None,
                                        request_app=request_app,
                                        app=app)
        filtered_apps.append((filtered_request_app, app))

    joined_request = request_parser.join(filtered_apps)
    return upstream_request(joined_request, run_filters=False)
