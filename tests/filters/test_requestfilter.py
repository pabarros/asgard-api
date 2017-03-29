from unittest import TestCase
import mock

from hollowman.app import application
from hollowman.filters.request import RequestFilter, _get_ctx, _build_filters_list
from hollowman.filters.dns import DNSRequestFilter

from flask import request
from marathon.models.app import MarathonApp
import json
from os import environ

class RequestFilterTest(TestCase):

    def test_production_filters_have_attr_name(self):
        for f in _build_filters_list():
            self.assertTrue(hasattr(f, 'name'))

    def test_dispatch_one_filter(self):
        """
        Tests if the run() method of the Filter is called
        """
        _filters = [mock.MagicMock()]
        with mock.patch("hollowman.filters.request._filters", _filters):
            final_request = RequestFilter.dispatch(None)
            self.assertIsNone(final_request)
            self.assertTrue(_filters[0].run.called)

    def test_dispatch_popultates_ctx_with_the_request_object(self):
        class RequestObject(object):
            foo = "bar"

        filters = [mock.MagicMock(), mock.MagicMock()]
        with mock.patch("hollowman.filters.request._filters", filters):
            request = RequestObject()
            final_request = RequestFilter.dispatch(request)
            self.assertIsNotNone(final_request)
            self.assertEqual(final_request, request)
            for f in filters:
                context_param = f.run.call_args[0][0]
                self.assertTrue(hasattr(
                    context_param,
                    "request"
                ))
                self.assertTrue(context_param.request.foo == "bar")

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

    def test_build_filters_list(self):
        import hollowman
        self.assertTrue(len(hollowman.filters.request._filters) > 1)

    def test_do_not_add_dns_filter_if_filter_is_disabled(self):
        new_env = {}
        new_env["{prefix}"]
        with mock.patch.dict(environ, {"foo":"bar"}):
            import ipdb; ipdb.set_trace()
            filters = request._build_filters_list()
            dns_filter_included = [isinstance(filter_, DNSRequestFilter) for filter_ in filters]
            self.assertFalse(any(dns_filter_included), "DNSRequestFilter esta na lista de filtros desligados, nao deveria")
