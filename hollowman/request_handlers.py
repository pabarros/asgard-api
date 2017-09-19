from flask import Response

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

    r = upstream.replay_request(modded_request, conf.MARATHON_ENDPOINT)
    return Response(response=r.content,
                    status=r.status_code,
                    headers=dict(r.headers))


def new(request: HollowmanRequest) -> Response:
    # does nothing for now
    return old(request)
