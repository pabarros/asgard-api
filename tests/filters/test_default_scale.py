from unittest import TestCase
import mock

from marathon.models.app import MarathonApp
from hollowman.filters.default_scale import DefaultScaleRequestFilter
from tests import RequestStub
from os import getcwd
from json import loads

from hollowman.filters import Context
from hollowman.filters.default_scale import DefaultScaleRequestFilter

class DefaultScaleRequestFilterTest(TestCase):

    def setUp(self):
        self.ctx = Context(marathon_client=None, request=None)
        self.filter = DefaultScaleRequestFilter()

    def test_suspend_a_running_app(self):
        _data = {
            "instances": 0
        }
        request = RequestStub(
            data=_data,
            method='PUT',
            path='/v2/apps//foo'
        )

        with mock.patch.object(self, "ctx") as ctx_mock:
            ctx_mock.marathon_client.get_app.return_value = MarathonApp(instances=2)
            self.ctx.request = request
            result_request = self.filter.run(self.ctx)

            ctx_mock.marathon_client.get_app.assert_called_with("/foo")
            self.assertTrue('labels' in result_request.get_json())
            self.assertEqual("2", result_request.get_json()['labels']['hollowman.default_scale'])


    def test_suspend_a_running_app_with_labels(self):
        _data = {
            "instances": 0,
            "labels": {
                "owner": "zeus"
            }
        }
        request = RequestStub(
            data=_data,
            method='POST',
            path='/v2/apps//foo'
        )

        with mock.patch.object(self, "ctx") as ctx_mock:
            ctx_mock.marathon_client.get_app.return_value = MarathonApp(instances=3)
            self.ctx.request = request
            result_request = self.filter.run(self.ctx)

            ctx_mock.marathon_client.get_app.assert_called_with("/foo")
            self.assertTrue('labels' in result_request.get_json())
            self.assertEqual("3", result_request.get_json()['labels']['hollowman.default_scale'])
            self.assertEqual("zeus", result_request.get_json()['labels']['owner'])

    def test_suspend_and_already_suspended_app(self):
        """
        In this case we must not override the value o labels.hollowman.default_scale.
        """
        _data = {
            "instances": 0
        }
        request = RequestStub(
            data=_data,
            method='POST',
            path='/v2/apps//foo'
        )

        with mock.patch.object(self, "ctx") as ctx_mock:
            ctx_mock.marathon_client.get_app.return_value = MarathonApp(instances=0)
            self.ctx.request = request
            result_request = self.filter.run(self.ctx)
            self.assertFalse('labels' in result_request.get_json())

        with mock.patch.object(self, "ctx") as ctx_mock:
            ctx_mock.marathon_client.get_app.return_value = MarathonApp()
            self.ctx.request = request
            result_request = self.filter.run(self.ctx)
            self.assertFalse('labels' in result_request.get_json())

    def test_create_label_on_app_without_labels(self):
        _data = {
            "instances": 0
        }
        request = RequestStub(
            data=_data,
            method='PUT',
            path='/v2/apps//foo'
        )

        with mock.patch.object(self, "ctx") as ctx_mock:
            ctx_mock.marathon_client.get_app.return_value = MarathonApp(instances=2)
            self.ctx.request = request
            result_request = self.filter.run(self.ctx)

            ctx_mock.marathon_client.get_app.assert_called_with("/foo")
            self.assertTrue('labels' in result_request.get_json())
            self.assertEqual("2", result_request.get_json()['labels']['hollowman.default_scale'])

