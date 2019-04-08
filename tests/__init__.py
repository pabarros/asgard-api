# encoding: utf-8

import json

from asgard.models.base import BaseModelAlchemy
from hollowman.models import engine


class RequestStub(object):
    def __init__(
        self, data=None, headers=None, is_json=True, method="GET", path=None
    ):
        self.data = json.dumps(data)
        self.headers = headers
        self.is_json = is_json
        self.method = method
        self.path = path

    def get_json(self):
        return json.loads(self.data)
