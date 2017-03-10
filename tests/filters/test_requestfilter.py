from unittest import TestCase
import mock

from hollowman.app import application
from hollowman.filters.request import RequestFilter

from flask import request
from marathon.models.app import MarathonApp
import json

class RequestFilterTest(TestCase):

    def test_dispatch_one_filter(self):
        """
        Tests if the run() method of the Filter is called
        """
        class FilterOne(object):

            def run(self, r):
                self.filter_called = True
                return r
        filter_one = FilterOne()
        with mock.patch("hollowman.filters.request._filters", [filter_one]):
            final_request = RequestFilter.dispatch(None)
            self.assertIsNone(final_request)
            self.assertTrue(filter_one.filter_called)

    def test_dispatch_popultates_ctx_with_the_request_object(self):
        class RequestObject(object):
            filter_one = None
            filter_two = None

        class FilterOne(object):

            def run(self, ctx):
                ctx.request.filter_one = True
                return ctx.request

        class FilterTwo(object):

            def run(self, ctx):
                ctx.request.filter_two = True
                return ctx.request

        filters = [FilterOne(), FilterTwo()]
        with mock.patch("hollowman.filters.request._filters", filters):
            request = RequestObject()
            final_request = RequestFilter.dispatch(request)
            self.assertIsNotNone(final_request)
            self.assertTrue(request.filter_one)
            self.assertTrue(request.filter_two)

    def test_dispatch_all_filters_empty_body(self):
        """
        Tests if we can run all filters with empty
        """
        with application.test_request_context(
                '/v2/apps/foo/restart',
                data='',
                content_type="application/json"):
            try:
                RequestFilter.dispatch(request)
            except Exception as e:
                import traceback
                traceback.print_exc()
                self.fail("Nao deveria ter dado exception, %s" % e)


    def test_dispatch_all_filters_with_incomplete_body(self):
        """
        Tests if we can run all filters with an incomplete body, which force them to
        pull the original app from Marathon
        """
        with application.test_request_context(
                '/v2/apps/foo/restart',
                data='{"insances": 30}',
                content_type="application/json"):

            try:
                import hollowman.filters
                with mock.patch.object(hollowman.filters.BaseFilter, "get_original_app") as get_original_app_mock, \
                        mock.patch.object(hollowman.filters.request, "_get_ctx") as get_ctx_mock:
                    #import ipdb; ipdb.set_trace()
                    ctx_mock = mock.MagicMock()
                    ctx_mock.request = request
                    get_ctx_mock.return_value = ctx_mock
                    get_original_app_mock.return_value = MarathonApp(**json.loads(open("json/single_full_app.json").read()))

                    RequestFilter.dispatch(request)

                    call_list = get_original_app_mock.call_args_list
                    for effective_call in call_list:
                        self.assertEqual(mock.call(ctx_mock), effective_call, "Alguma chamada nao passou ctx para self.get_original_all()")
            except Exception as e:
                import traceback
                traceback.print_exc()
                self.fail("Nao deveria ter dado exception, %s" % e)
