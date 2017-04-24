# encoding: utf-8

import json

from hollowman.filters import BaseFilter
from hollowman.options import get_option

from marathon.models.constraint import MarathonConstraint


class BaseConstraintFilter(BaseFilter):

    name = 'constraint'

    def run(self, ctx):
        request = ctx.request
        if request.is_json and request.data:
            data = request.get_json()

            if self.is_single_app(data):
                originial_app = self.get_original_app(ctx)
                app_dict = json.loads(originial_app.to_json())
                app_dict.update(data)

                base_constraint_options = get_option(self.name, "BASECONSTRAINT")
                base_constraints = []
                for constraint in base_constraint_options:
                    base_constraints.append(MarathonConstraint(*constraint.split(":")))

                if not originial_app.constraints:
                    app_dict['constraints'] = [c.json_repr() for c in base_constraints]

                if not data.get('constraints'):
                    app_dict['constraints'] = [c.json_repr() for c in base_constraints]

                request.data = json.dumps(app_dict)

        return request
