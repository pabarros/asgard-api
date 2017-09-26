from unittest import TestCase
from unittest.mock import patch, Mock

from hollowman.filters.dummy import DummyLogFilter


class DummyLogFilterTests(TestCase):
    def setUp(self):
        self.filter = DummyLogFilter()

    def tearDown(self):
        patch.stopall()

    def test_read_returns_the_unmodified_request(self):
        request_app = Mock()
        result = self.filter.read(None, request_app, None)

        self.assertEqual(result, request_app)

    def test_write_logs_request_to_output(self):
        request_app = Mock()
        result = self.filter.write(None, request_app, None)

        self.assertEqual(result, request_app)
