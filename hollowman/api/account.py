
import json
from flask import request, Blueprint, make_response

from hollowman.decorators import auth_required
from hollowman.auth.jwt import jwt_auth

account_blueprint = Blueprint(__name__, __name__)


def _generate_repsonse(user_info, extra_headers):
    response_body = json.dumps(user_info)
    response = make_response(response_body, 200)
    for k, v in extra_headers.items():
        response.headers[k] = v
    return response


def _generate_user_info(user, current_account):
    return {
        "user": {
            "email": user.tx_email,
            "name": user.tx_name
        },
        "current_account": {
            "id": current_account.id,
            "name": current_account.name
        }
    }

@account_blueprint.route("/me", methods=["GET"])
@auth_required()
def me():
    return json.dumps(_generate_user_info(request.user, request.user.current_account))

@account_blueprint.route("/change/<int:acc_id>", methods=["POST"])
@auth_required()
def change_account(acc_id):
    account_ids = [acc.id for acc in request.user.accounts]
    try:
        user_info = _generate_user_info(request.user, request.user.accounts[account_ids.index(acc_id)])
        jwt_token = jwt_auth.jwt_encode_callback(user_info)
        return _generate_repsonse(user_info, {"X-JWT": jwt_token})
    except ValueError:
        pass

    return make_response(json.dumps({"msg": "Not associated with account"}), 401)

@account_blueprint.route("/next", methods=["POST"])
@auth_required()
def next_account():
    account_ids = [acc.id for acc in request.user.accounts]
    current_account_position = account_ids.index(request.user.current_account.id)
    if current_account_position < len(account_ids) - 1:
        return change_account(request.user.accounts[current_account_position + 1].id)
    return change_account(request.user.accounts[0].id)

