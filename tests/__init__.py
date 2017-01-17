#encoding: utf-8

import json

class RequestStub(object):

    def __init__(self, data=None, headers=None, is_json=True):
        self.data = json.dumps(data)
        self.headers = headers
        self.is_json = is_json

    def get_json(self):
        return json.loads(self.data)
