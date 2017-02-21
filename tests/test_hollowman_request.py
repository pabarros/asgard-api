from unittest import TestCase
from hollowman.app import application
from flask import request
import json

# from flask.wrappers import Request


class TestHollowmanRequest(TestCase):

    # see: http://flask.pocoo.org/docs/0.12/testing/#other-testing-tricks
    def test_default_cache_disabled(self):
        with application.test_request_context(
                '/v2/apps/foo',
                data='{"foo":"bar"}',
                content_type="application/json"):
            json1 = request.get_json()
            request.data = '{"abc":123}'
            json2 = request.get_json()
            self.assertNotEqual(json1, json2)
