from marathon.models.constraint import MarathonConstraint


class AddOwnerConstraintFilter:
    name = "owner"

    def write(self, user, request_app, original_app):

        owner_constraint = MarathonConstraint(
            field="owner", operator="LIKE", value=user.current_account.owner
        )
        if request_app.has_constraint("owner"):
            request_app.remove_constraints_by_name("owner")

        request_app.constraints.append(owner_constraint)
        return request_app
