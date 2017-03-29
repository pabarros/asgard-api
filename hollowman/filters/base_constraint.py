# encoding: utf-8

import json
from hollowman.filters import BaseFilter


DEFAULT_CONSTRAINT_DC = [ "dc", "LIKE", "sl", ]
DEFAULT_CONSTRAINT_EXCLUSIVE = [ "exclusive", "UNLIKE", ".*" ]

class BaseConstraintFilter(BaseFilter):

    name = 'base_constraint'

    def run(self, ctx):
        request = ctx.request
        if request.is_json and request.data:
            data = request.get_json()

            if self.is_single_app(data):
                originial_app = self.get_original_app(ctx)
                app_dict = json.loads(originial_app.to_json())
                app_dict.update(data)

                if not originial_app.constraints:
                    app_dict['constraints'] = [
                        DEFAULT_CONSTRAINT_EXCLUSIVE,
                        DEFAULT_CONSTRAINT_DC,
                    ]
                elif originial_app.constraints \
                        and "dc" not in [c.field for c in originial_app.constraints]:
                    app_dict['constraints'].append(DEFAULT_CONSTRAINT_DC)

                request.data = json.dumps(app_dict)

        return request
