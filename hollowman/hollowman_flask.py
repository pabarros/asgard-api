from flask import Flask,Request

class HollowmanRequest(Request):

    def get_json(self, force=False, silent=False, cache=False):
        """
        Changed cache to False to ease filter implementations
        """
        return super(Request, self).get_json(
            force,
            silent,
            cache
        )

#  See: http://flask.pocoo.org/docs/0.12/patterns/subclassing/
class HollowmanFlask(Flask):
    request_class = HollowmanRequest
