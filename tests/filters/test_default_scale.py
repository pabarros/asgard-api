from unittest import TestCase
import mock

from marathon.models.app import MarathonApp
from hollowman.filters.default_scale import DefaultScaleRequestFilter
from tests import RequestStub
from os import getcwd
from json import loads

from hollowman.filters.request import _ctx
from hollowman.filters.default_scale import DefaultScaleRequestFilter

class DefaultScaleRequestFilterTest(TestCase):

    def setUp(self):
        self.filter = DefaultScaleRequestFilter(_ctx)

    def test_suspend_a_running_app(self):
        _data = {
            "instances": 0
        }
        request = RequestStub(
            data=_data,
            method='PUT',
            path='/v2/apps//foo'
        )

        with mock.patch.object(self.filter, "ctx") as ctx_mock:
            ctx_mock.marathon_client.get_app.return_value = MarathonApp(instances=2)
            result_request = self.filter.run(request)

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

        with mock.patch.object(self.filter, "ctx") as ctx_mock:
            ctx_mock.marathon_client.get_app.return_value = MarathonApp(instances=3)
            result_request = self.filter.run(request)

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

        with mock.patch.object(self.filter, "ctx") as ctx_mock:
            ctx_mock.marathon_client.get_app.return_value = MarathonApp(instances=0)
            result_request = self.filter.run(request)
            self.assertFalse('labels' in result_request.get_json())

        with mock.patch.object(self.filter, "ctx") as ctx_mock:
            ctx_mock.marathon_client.get_app.return_value = MarathonApp()
            result_request = self.filter.run(request)
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

        with mock.patch.object(self.filter, "ctx") as ctx_mock:
            ctx_mock.marathon_client.get_app.return_value = MarathonApp(instances=2)
            result_request = self.filter.run(request)

            self.assertTrue('labels' in result_request.get_json())
            self.assertEqual("2", result_request.get_json()['labels']['hollowman.default_scale'])

    def test_get_current_scale(self):
        with mock.patch.object(self.filter, "ctx") as ctx_mock:
            ctx_mock.marathon_client.get_app.return_value = MarathonApp(instances=2)
            current_scale = self.filter.get_current_scale('/foo')
            self.assertEqual(current_scale, 2)

