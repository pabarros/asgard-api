import json

from flask import Blueprint, make_response, request

from hollowman.auth.jwt import jwt_auth, jwt_generate_user_info
from hollowman.decorators import auth_required

account_blueprint = Blueprint(__name__, __name__)


def _generate_repsonse(user_info, new_jwt_token):
    user_info["jwt_token"] = new_jwt_token
    response_body = json.dumps(user_info)
    response = make_response(response_body, 200)
    return response


@account_blueprint.route("/me", methods=["GET"])
@auth_required()
def me():
    return json.dumps(
        jwt_generate_user_info(request.user, request.user.current_account)
    )


@account_blueprint.route("/change/<int:acc_id>", methods=["POST"])
@auth_required()
def change_account(acc_id):
    account_ids = [acc.id for acc in request.user.accounts]
    try:
        user_info = jwt_generate_user_info(
            request.user, request.user.accounts[account_ids.index(acc_id)]
        )
        jwt_token = jwt_auth.jwt_encode_callback(user_info)
        return _generate_repsonse(user_info, jwt_token.decode("utf8"))
    except ValueError:
        pass

    return make_response(
        json.dumps({"msg": "Not associated with account"}), 401
    )


@account_blueprint.route("/next", methods=["POST"])
@auth_required()
def next_account():
    account_ids = [acc.id for acc in request.user.accounts]
    current_account_position = account_ids.index(
        request.user.current_account.id
    )
    if current_account_position < len(account_ids) - 1:
        return change_account(
            request.user.accounts[current_account_position + 1].id
        )
    return change_account(request.user.accounts[0].id)
