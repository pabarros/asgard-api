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
        with mock.patch.object(self, "ctx") as ctx_mock, \
                mock.patch.dict('os.environ', {
                    "HOLLOWMAN_FILTER_CONSTRAINT_PARAM_BASECONSTRAINT_0": "exclusive:UNLIKE:.*",
                    "HOLLOWMAN_FILTER_CONSTRAINT_PARAM_BASECONSTRAINT_1": "dc:LIKE:sl"
                }) as environ_mock:
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
                        ],
                        [
                            "dc",
                            "LIKE",
                            "sl",

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

    def test_simple_app_with_dc_constraint(self):
        """
        Se uma app ja possui a constraint "dc" não mexemos nas constraints
        """
        data = {
            "id": "/foo/bar",
            "constraints": [
                [
                    "exclusive",
                    "LIKE",
                    "web"
                ],
                [
                    "dc",
                    "LIKE",
                    "(sl|aws)",
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
                        ],
                        [
                            "dc",
                            "LIKE",
                            "(sl|aws)"
                        ]
                    ]
                }
            )

    def test_original_app_with_constraint_payload_without(self):
        """
        Se uma app originalmente possui alguma constraint, mas o payload que está
        chegando no request está sem nada, devemos colocar as constraints default
        """
        data = {
            "id": "/foo/bar",
            "constraints": [
                [
                    "exclusive",
                    "LIKE",
                    "web"
                ],
                [
                    "dc",
                    "LIKE",
                    "(sl|aws)",
                ]
            ]
        }

        from marathon.models.app import MarathonApp
        with mock.patch.object(self, "ctx") as ctx_mock, \
                mock.patch.dict('os.environ', {
                    "HOLLOWMAN_FILTER_CONSTRAINT_PARAM_BASECONSTRAINT_0": "exclusive:UNLIKE:.*",
                    "HOLLOWMAN_FILTER_CONSTRAINT_PARAM_BASECONSTRAINT_1": "dc:LIKE:sl"
                }) as env_mock:
            request = RequestStub(path="/v2/apps//app/foo", data={u"id": "/foo/bar", u"mem": 32}, method="PUT")
            ctx_mock.marathon_client.get_app.return_value = MarathonApp(**data)

            self.ctx.request = request
            modified_request = self.filter.run(self.ctx)
            self.assertEqual(
                {
                    u"id": u"/foo/bar",
                    u"mem": 32,
                    u"constraints": [
                        [
                            "exclusive",
                            "UNLIKE",
                            ".*"
                        ],
                        [
                            "dc",
                            "LIKE",
                            "sl"
                        ]
                    ]
                },
                modified_request.get_json()
            )
