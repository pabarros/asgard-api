from unittest import TestCase
from hollowman.app import application
from flask import request
import json

# from flask.wrappers import Request
from hollowman.hollowman_flask import OperationType


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


class TestOperations(TestCase):
    def test_GET_request_is_a_READ_operation(self):
        with application.test_request_context('/v2/apps/', method='GET'):
            operations = request.get_operations()

            self.assertIn(OperationType.READ, operations)
            self.assertNotIn(OperationType.WRITE, operations)

    def test_POST_request_is_a_WRITE_operation(self):
        with application.test_request_context('/v2/apps/', method='POST'):
            operations = request.get_operations()

            self.assertIn(OperationType.WRITE, operations)
            self.assertNotIn(OperationType.READ, operations)

    def test_PUT_request_is_a_WRITE_operation(self):
        with application.test_request_context('/v2/apps/', method='PUT'):
            operations = request.get_operations()

            self.assertIn(OperationType.WRITE, operations)
            self.assertNotIn(OperationType.READ, operations)

    def test_PATCH_request_is_a_WRITE_operation(self):
        with application.test_request_context('/v2/apps/', method='PATCH'):
            operations = request.get_operations()

            self.assertIn(OperationType.WRITE, operations)
            self.assertNotIn(OperationType.READ, operations)

    def test_DELETE_request_is_a_WRITE_operation(self):
        with application.test_request_context('/v2/apps/', method='DELETE'):
            operations = request.get_operations()

            self.assertIn(OperationType.WRITE, operations)
            self.assertNotIn(OperationType.READ, operations)
