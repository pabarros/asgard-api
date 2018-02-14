from marathon import MarathonConstraint

from hollowman.marathonapp import AsgardMarathonApp


class BasicConstraintFilter:
    mesos_constraint = MarathonConstraint.from_json('mesos:LIKE:slave'.split(':'))
    workload_constraint = MarathonConstraint.from_json('workload:LIKE:general'.split(':'))

    def write(self, user, request_app: AsgardMarathonApp, app):
        if not request_app.has_constraint(self.mesos_constraint.field):
            request_app.constraints.append(self.mesos_constraint)
        if not request_app.has_constraint(self.workload_constraint.field):
            request_app.constraints.append(self.workload_constraint)

        return request_app
