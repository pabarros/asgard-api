# encoding: utf-8

import json
from hollowman.filters import BaseFilter


class BaseConstraintFilter(BaseFilter):

    def __init__(self, ctx):
        super(BaseConstraintFilter, self).__init__(ctx)

    def run(self, request):
        if request.is_json and request.data:
            data = request.get_json()

            if self.is_single_app(data):
                origina_app = self.get_original_app(request)
                app_dict = json.loads(origina_app.to_json())

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
