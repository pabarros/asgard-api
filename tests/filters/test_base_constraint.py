#encoding: utf-8

from hollowman.filters.base_constraint import BaseConstraintFilter
from unittest import TestCase
from tests import RequestStub
from hollowman.filters.request import _ctx


class BaseConstraintFilterTest(TestCase):

    def setUp(self):
        self.filter = BaseConstraintFilter(_ctx)

    def test_simple_app(self):
        data = {"id": "/foo/bar"}
        request = RequestStub(data=data)
        modified_request = self.filter.run(request)

        self.assertEqual(
            modified_request.get_json(),
            {
                "id": "/foo/bar",
                "constraints": [
                    [
                        "exclusive",
                        "UNLIKE",
                        ".*"
                    ]
                ]
            }
        )

    def test_simple_app_with_constraints(self):
        data = {
            "id": "/foo/bar",
            "constraints": [
                [
                    "exclusive",
                    "LIKE",
                    "web"
                ]
            ]
        }
        request = RequestStub(data=data)
        modified_request = self.filter.run(request)

        self.assertEqual(
            modified_request.get_json(),
            {
                "id": "/foo/bar",
                "constraints": [
                    [
                        "exclusive",
                        "LIKE",
                        "web"
                    ]
                ]
            }
        )
