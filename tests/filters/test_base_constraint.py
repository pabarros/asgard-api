#encoding: utf-8

from hollowman.filters.base_constraint import BaseConstraintFilter
from unittest import TestCase
from tests import RequestStub
from hollowman.filters import Context

import mock

class BaseConstraintFilterTest(TestCase):

    def setUp(self):
        self.ctx = Context(marathon_client=None, request=None)
        self.filter = BaseConstraintFilter()

    def test_simple_app(self):
        data = {"id": "/foo/bar"}
        request = RequestStub(data=data)

        from marathon.models.app import MarathonApp
        with mock.patch.object(self, "ctx") as ctx_mock:
            request = RequestStub(path="/v2/apps//app/foo", data=data, method="PUT")
            ctx_mock.marathon_client.get_app.return_value = MarathonApp(**data)

            self.ctx.request = request
            filtered_request = self.filter.run(self.ctx)
            ctx_mock.marathon_client.get_app.assert_called_with("/app/foo")

            self.assertEqual(
                filtered_request.get_json(),
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

        from marathon.models.app import MarathonApp
        with mock.patch.object(self, "ctx") as ctx_mock:
            request = RequestStub(path="/v2/apps//app/foo", data=data, method="PUT")
            ctx_mock.marathon_client.get_app.return_value = MarathonApp(**data)

            self.ctx.request = request
            modified_request = self.filter.run(self.ctx)

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
