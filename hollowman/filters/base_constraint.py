# encoding: utf-8

import json
from hollowman.filters import BaseFilter


class BaseConstraintFilter(BaseFilter):

    def run(self, ctx):
        request = ctx.request
        if request.is_json and request.data:
            data = request.get_json()

            if self.is_single_app(data):
                app_dict = json.loads(self.get_original_app(ctx).to_json())
                app_dict.update(data)

                if 'constraints' not in app_dict or app_dict['constraints'] == []:
                    app_dict['constraints'] = [
                        [
                            "exclusive",
                            "UNLIKE",
                            ".*"
                        ]
                    ]

                request.data = json.dumps(app_dict)

        return request
