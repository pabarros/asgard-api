from flask import Response
from http import HTTPStatus

from hollowman.dispatcher import dispatch, dispatch_response_pipeline
from hollowman.hollowman_flask import HollowmanRequest
from hollowman import upstream, conf, http_wrappers
from hollowman.hollowman_flask import OperationType


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

    if OperationType.WRITE not in request.request.operations and response.status_code == HTTPStatus.OK:
        response_wrapper = http_wrappers.Response(request.request, response)
        final_response = dispatch_response_pipeline(user=_get_user_from_request(request.request),
                                                   response=response_wrapper)
        return final_response

    return response


def _get_user_from_request(request):
    try:
        return request.user
    except:
        return None
