#encoding: utf-8

import json
from marathon import MarathonClient
from hollowman.filters import BaseFilter


class DefaultScaleRequestFilter(BaseFilter):

    def run(self, ctx):
        request = ctx.request
        if request.is_json and request.data:
            data = json.loads(request.data)
            if self.is_single_app(data):
                original_app = self.get_original_app(ctx)
                original_app_dict = json.loads(original_app.to_json())
                current_app_scale = original_app.instances

                if data.get('instances', 1) == 0 and current_app_scale != 0 and current_app_scale is not None:
                    labels = data.get("labels", {})
                    labels.update({
                        'hollowman.default_scale': str(current_app_scale)
                    })
                    data['labels'] = labels

            original_app_dict.update(data)
            request.data = json.dumps(original_app_dict)

        return request

