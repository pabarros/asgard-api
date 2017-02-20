# encoding: utf-8

import json
from hollowman.filters import BaseFilter


class BaseConstraintFilter(BaseFilter):

    def __init__(self, ctx):
        super(BaseConstraintFilter, self).__init__(ctx)

    def run(self, request):
        if request.is_json and request.data:
            data = request.get_json()

            if self.is_single_app(data) and (('constraints' not in data)\
                or (data['constraints'] == [])):
                data['constraints'] = [
                    [
                        "exclusive",
                        "UNLIKE",
                        ".*"
                    ]
                ]

                request.data = json.dumps(data)

        return request
