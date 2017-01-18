from unittest import TestCase
import mock
from hollowman.filters.default_scale import DefaultScaleRequestFilter
from tests import RequestStub
from os import getcwd
from json import loads


class DefaultScaleRequestFilterTest(TestCase):

    def setUp(self):
        self.filter = DefaultScaleRequestFilter()
        self.marathon_client_patch = mock.patch('hollowman.filters.default_scale.MarathonClient')

        self.marathon_client_mock = self.marathon_client_patch.start()
        self.marathon_client_mock.return_value.get_app.return_value.instances = 2

    def tearDown(self):
        self.marathon_client_patch.stop()

    def test_run(self):
        _data = loads(open(getcwd()+'/../json/single_full_app.json').read())
        request = RequestStub(
            data=_data,
            method='POST',
            path='/v2/apps//foo'
        )

        result_request = self.filter.run(request)

        self.assertTrue('labels' in result_request.get_json())
        self.assertEqual(2, result_request.get_json()['labels']['default_scale'])

    def test_get_current_scale(self):
        current_scale = self.filter.get_current_scale('/foo')
        self.assertEqual(current_scale, 2)

    def test_get_app_id(self):
        self.assertEqual('/foo', self.filter.get_app_id('/v2/apps//foo'))
        self.assertEqual('/foo/taz/bar', self.filter.get_app_id('/v2/apps//foo/taz/bar'))
