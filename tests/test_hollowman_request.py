import json
from unittest import TestCase

from flask import request

from hollowman.app import application
from hollowman.hollowman_flask import OperationType


class TestHollowmanRequest(TestCase):

    # see: http://flask.pocoo.org/docs/0.12/testing/#other-testing-tricks
    def test_default_cache_disabled(self):
        with application.test_request_context(
            "/v2/apps/foo",
            data='{"foo":"bar"}',
            content_type="application/json",
        ):
            json1 = request.get_json()
            request.data = '{"abc":123}'
            json2 = request.get_json()
            self.assertNotEqual(json1, json2)


class TestOperations(TestCase):
    def test_GET_request_is_a_READ_operation(self):
        with application.test_request_context("/v2/apps/", method="GET"):
            self.assertIn(OperationType.READ, request.operations)
            self.assertNotIn(OperationType.WRITE, request.operations)

    def test_POST_request_is_a_WRITE_operation(self):
        with application.test_request_context("/v2/apps/", method="POST"):
            self.assertIn(OperationType.WRITE, request.operations)
            self.assertNotIn(OperationType.READ, request.operations)

    def test_PUT_request_is_a_WRITE_operation(self):
        with application.test_request_context("/v2/apps/", method="PUT"):
            self.assertIn(OperationType.WRITE, request.operations)
            self.assertNotIn(OperationType.READ, request.operations)

    def test_PATCH_request_is_a_WRITE_operation(self):
        with application.test_request_context("/v2/apps/", method="PATCH"):
            self.assertIn(OperationType.WRITE, request.operations)
            self.assertNotIn(OperationType.READ, request.operations)

    def test_DELETE_request_is_a_WRITE_operation(self):
        with application.test_request_context("/v2/apps/", method="DELETE"):
            self.assertIn(OperationType.WRITE, request.operations)
            self.assertNotIn(OperationType.READ, request.operations)
