from unittest import TestCase
import mock

from marathon.models.app import MarathonApp
from hollowman.filters.default_scale import DefaultScaleRequestFilter
from tests import RequestStub
from os import getcwd
from json import loads

from hollowman.filters.default_scale import DefaultScaleRequestFilter
from hollowman import conf
from hollowman.filters import Context

class DefaultScaleRequestFilterTest(TestCase):

    def setUp(self):
        self.marathon_client_patch = mock.patch.object(conf, 'marathon_client')

        self.marathon_client_mock = self.marathon_client_patch.start()
        full_app_data = loads(open('json/single_full_app.json').read())
        self.marathon_client_mock.return_value.get_app.return_value = MarathonApp(**full_app_data)
        self.marathon_client_mock.get_app.return_value.instances = 2
        self.filter = DefaultScaleRequestFilter(Context(self.marathon_client_mock))

    def tearDown(self):
        self.marathon_client_patch.stop()

    def test_suspend_a_running_app(self):
        _data = {
            "instances": 0
        }
        request = RequestStub(
            data=_data,
            method='POST',
            path='/v2/apps//foo'
        )

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

        result_request = self.filter.run(request)

        self.assertTrue('labels' in result_request.get_json())
        self.assertEqual("2", result_request.get_json()['labels']['hollowman.default_scale'])
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

        current_app_data = {
            "instances": 0,
            "id": "/foo"
        }
        marathon_client_mock = mock.MagicMock()
        marathon_client_mock.get_app.return_value = MarathonApp(**current_app_data)

        default_scale_filter = DefaultScaleRequestFilter(Context(marathon_client=marathon_client_mock))
        result_request = default_scale_filter.run(request)

        self.assertFalse('labels' in result_request.get_json())

    def test_create_label_on_app_without_labels(self):
        _data = {
            "instances": 0
        }
        request = RequestStub(
            data=_data,
            method='POST',
            path='/v2/apps//foo'
        )

        result_request = self.filter.run(request)

        self.assertTrue('labels' in result_request.get_json())
        self.assertEqual("2", result_request.get_json()['labels']['hollowman.default_scale'])

    def test_get_current_scale(self):
        current_scale = self.filter.get_current_scale('/foo')
        self.assertEqual(current_scale, 2)

