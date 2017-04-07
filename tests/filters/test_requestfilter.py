from unittest import TestCase
import mock
import os

from hollowman.app import application
from hollowman.filters import BaseFilter
from hollowman.filters.request import RequestFilter, _get_ctx, _build_filters_list
from hollowman.filters.dns import DNSRequestFilter
from hollowman.filters.appname import AddAppNameFilter

from flask import request
from marathon.models.app import MarathonApp
import json
from os import environ
from hollowman.conf import ConfHelper

class RequestFilterTest(TestCase):

    def test_production_filters_have_attr_name(self):
        for f in _build_filters_list():
            self.assertTrue(hasattr(f, 'name'))

    def test_dispatch_one_filter(self):
        """
        Tests if the run() method of the Filter is called
        """

        f1 = mock.MagicMock()
        f1.name = 'foo'

        _filters = [f1]
        with mock.patch("hollowman.filters.request._filters", _filters):
            final_request = RequestFilter.dispatch(None)
            self.assertIsNone(final_request)
            self.assertTrue(_filters[0].run.called)


    def test_dispatch_popultates_ctx_with_the_request_object(self):
        class RequestObject(object):
            filter_one = None
            filter_two = None

        class FilterOne(BaseFilter):
            name = "one"

            def run(self, ctx):
                ctx.request.filter_one = True
                return ctx.request

        class FilterTwo(BaseFilter):
            name = "two"

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

    def test_build_filters_all_enabled(self):
        import hollowman
        all_filters = _build_filters_list()
        self.assertEqual(len(hollowman.filters.request._filters), len(all_filters))

    def test_build_filters_dns_globally_disabled(self):
        with mock.patch.object(os, 'getenv') as getenv_mock:
            def _side_effect(arg):
                _data = {"HOLLOWMAN_FILTER_DNS_DISABLE": "any-value"}
                return _data.get(arg)

            getenv_mock.side_effect = _side_effect
            all_filters = _build_filters_list()
            self.assertTrue(len(all_filters) > 0)
            self.assertFalse(any([isinstance(f, DNSRequestFilter) for f in all_filters]), "DNSRequestFilter nao deveria estar ligado")


    def test_build_filters_appname_globally_disabled(self):
        with mock.patch.object(os, 'getenv') as getenv_mock:
            def _side_effect(arg):
                _data = {"HOLLOWMAN_FILTER_APPNAME_DISABLE": "any-value"}
                return _data.get(arg)

            getenv_mock.side_effect = _side_effect
            all_filters = _build_filters_list()
            self.assertTrue(len(all_filters) > 0)
            self.assertFalse(any([isinstance(f, AddAppNameFilter) for f in all_filters]), "AddAppNameFilter nao deveria estar ligado")
