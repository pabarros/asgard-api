from flask import Response

from hollowman.dispatcher import dispatch
from hollowman.hollowman_flask import HollowmanRequest
from hollowman import upstream, conf, http_wrappers


def upstream_request(request: HollowmanRequest, run_filters=True) -> Response:
    resp = upstream.replay_request(request, conf.MARATHON_ENDPOINT)
    return Response(response=resp.content,
                    status=resp.status_code,
                    headers=dict(resp.headers))


def new(request: http_wrappers.Request) -> Response:

    filtered_apps = []
    for request_app, app in request.split():
        filtered_request_app = dispatch(operations=request.request.operations,
                                        user=_get_user_from_request(request.request),
                                        request_app=request_app,
                                        app=app)
        filtered_apps.append((filtered_request_app, app))

    joined_request = request.join(filtered_apps)
    response = upstream_request(joined_request, run_filters=False)
    response_wrapper = http_wrappers.Response(request.request, response)

    return response


def _get_user_from_request(request):
    try:
        return request.user
    except:
        return None
