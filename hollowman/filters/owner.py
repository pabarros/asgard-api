

from marathon.models.constraint import MarathonConstraint

class AddOwnerConstraintFilter():
    name = "owner"

    def write(self, user, request_app, original_app):
        owner_constraint = MarathonConstraint(field="owner", operator="LIKE", value=user.current_account.owner)
        current_owner_constraint = request_app.get_constraint_by_name("owner")
        if current_owner_constraint:
            request_app.remove_constraint_by_name("owner")

        request_app.constraints.append(owner_constraint)
        return request_app
