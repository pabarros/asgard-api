from marathon import MarathonConstraint


class BasicConstraintFilter:
    constraints = (
        MarathonConstraint.from_json('mesos:LIKE:slave'.split(':')),
        MarathonConstraint.from_json('workload:LIKE:general'.split(':'))
    )

    def write(self, user, request_app, app):
        if request_app.constraints:
            return request_app

        request_app.constraints = list(self.constraints)
        return request_app
