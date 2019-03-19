from typing import List

from aiohttp.web import json_response
from asyncworker import RouteTypes

from asgard.app import app
from asgard.http.auth import auth_required
from asgard.http.auth.auth_required import _get_account_by_id
from asgard.models.account import Account
from asgard.models.user import User


@app.route(["/users/me"], type=RouteTypes.HTTP, methods=["GET"])
@auth_required
async def whoami(request):
    user = request.user
    current_account = user.current_account

    alternate_account_ids: List[int] = []
    alternate_account_ids = filter(
        lambda acc_id: acc_id != current_account.id, user.account_ids
    )

    alternate_accounts = [
        await _get_account_by_id(acc_id) for acc_id in alternate_account_ids
    ]

    return json_response(
        {
            "name": request.user.tx_name,
            "email": request.user.tx_email,
            "current_account": {
                "id": request.user.current_account.id,
                "name": request.user.current_account.name,
            },
            "accounts": [
                {"id": acc.id, "name": acc.name} for acc in alternate_accounts
            ],
        }
    )
