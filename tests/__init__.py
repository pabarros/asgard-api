#encoding: utf-8

import json

from hollowman.models import BaseModel, engine

class RequestStub(object):

    def __init__(self,
                data=None,
                headers=None,
                is_json=True,
                method='GET',
                path=None
    ):
        self.data = json.dumps(data)
        self.headers = headers
        self.is_json = is_json
        self.method = method
        self.path = path

    def get_json(self):
        return json.loads(self.data)

class ContextStub(object):

    def __init__(self, marathon_client=None):
        self.marathon_client = marathon_client


def rebuild_schema():
    assert engine.name == "sqlite"
    BaseModel.metadata.drop_all(engine)
    BaseModel.metadata.create_all(engine)

