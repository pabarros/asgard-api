from flask import Flask,Request
from json import loads

class HollowmanRequest(Request):

    def get_json(self, cache=False, **kwargs):
        """
        Changed cache to False to ease filter implementations
        """
        return loads(self.data)
        # return super(HollowmanRequest, self).get_json(
        #     cache=False,
        #     **kwargs
        # )

#  See: http://flask.pocoo.org/docs/0.12/patterns/subclassing/
class HollowmanFlask(Flask):
    request_class = HollowmanRequest
