from flask import Response

from hollowman.dispatcher import dispatch
from hollowman.parsers import RequestParser
from hollowman.hollowman_flask import HollowmanRequest
from hollowman import upstream, conf
from hollowman.filters.request import RequestFilter


def old(request: HollowmanRequest) -> Response:
    modded_request = request
    try:
        modded_request = RequestFilter.dispatch(request)
    except Exception:
        import traceback
        traceback.print_exc()

    resp = upstream.replay_request(modded_request, conf.MARATHON_ENDPOINT)
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
    return old(joined_request)
