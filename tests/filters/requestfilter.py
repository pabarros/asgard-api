from unittest import TestCase
import mock

from hollowman.filters.request import RequestFilter


class RequestFilterTest(TestCase):

  def test_dispatch_one_filter(self):
    """
    Tests if the run() method of the Filter is called
    """
    class FilterOne(object):
        def run(self, r):
            self.filter_called = True
            return r
    filter_one = FilterOne();
    with mock.patch("hollowman.filters.request._filters", [filter_one]):
        final_request = RequestFilter.dispatch(None)
        self.assertIsNone(final_request)
        self.assertTrue(filter_one.filter_called)

  def test_dispatch_chain_return_value_of_one_filter_to_the_next(self):
    """
    Tests if the return value of a filter is passed to the next one
    """
    class FilterOne(object):
        def run(self, r):
            r['filter_one'] = True
            return r

    class FilterTwo(object):
        def run(self, r):
            r['filter_two'] = True
            return r
    filters = [FilterOne(), FilterTwo()]
    with mock.patch("hollowman.filters.request._filters", filters):
        final_request = RequestFilter.dispatch({})
        self.assertIsNotNone(final_request)
        self.assertTrue(final_request['filter_one'])
        self.assertTrue(final_request['filter_two'])
