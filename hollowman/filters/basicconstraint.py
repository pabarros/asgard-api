from marathon import MarathonConstraint


class BasicConstraintFilter:
    mesos_constraint = MarathonConstraint.from_json('mesos:LIKE:slave'.split(':'))
    workload_constraint = MarathonConstraint.from_json('workload:LIKE:general'.split(':'))

    constraints = (mesos_constraint, workload_constraint)

    def write(self, user, request_app, app):
        if not request_app.constraints:
            request_app.constraints = list(self.constraints)
            return request_app

        has_mesos_constraint, has_workload_constraint = False, False
        for constraint in request_app.constraints:
            if constraint.field == self.mesos_constraint.field:
                has_mesos_constraint = True
            elif constraint.field == self.workload_constraint.field:
                has_workload_constraint = True

        if not has_mesos_constraint:
            request_app.constraints.append(self.mesos_constraint)
        if not has_workload_constraint:
            request_app.constraints.append(self.workload_constraint)

        return request_app
