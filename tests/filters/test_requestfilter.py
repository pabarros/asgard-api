#encoding: utf-8
from unittest import TestCase
import mock
import os

from hollowman.app import application
from hollowman.filters import BaseFilter
from hollowman.filters.request import RequestFilter, _get_ctx, _build_filters_list
from hollowman.filters.dns import DNSRequestFilter
from hollowman.filters.appname import AddAppNameFilter
import hollowman.filters

from flask import request
from marathon.models.app import MarathonApp
import json
from os import environ
from tests import RequestStub

class RequestFilterTest(TestCase):

    def test_dispatch_one_filter(self):
        """
        Tests if the run() method of the Filter is called
        """
        class FilterOne(BaseFilter):
            name = "one"

            def run(self, r):
                self.filter_called = True
                return r
        filter_one = FilterOne()
        with mock.patch("hollowman.filters.request._filters", [filter_one]):
            #import ipdb; ipdb.set_trace()
            final_request = RequestFilter.dispatch(RequestStub(data={}))
            self.assertIsNotNone(final_request)
            self.assertTrue(filter_one.filter_called)

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
            request = RequestStub(data={})
            final_request = RequestFilter.dispatch(request)
            self.assertIsNotNone(final_request)
            self.assertTrue(request.filter_one)
            self.assertTrue(request.filter_two)

    def test_dispatch_all_filters_empty_body(self):
        """
        Tests if we can run all filters with empty body
        """
        with application.test_request_context(
                '/v2/apps/foo/restart',
                data='{}',
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
                data='{"instances": 30}',
                content_type="application/json"):

            try:
                with mock.patch.object(hollowman.filters.BaseFilter, "get_original_app") as get_original_app_mock, \
                        mock.patch.object(hollowman.filters.request, "_get_ctx") as get_ctx_mock:
                    ctx_mock = mock.MagicMock()
                    ctx_mock.request = request
                    get_ctx_mock.return_value = ctx_mock
                    get_original_app_mock.return_value = MarathonApp(**json.loads(open("tests/fixtures/single_full_app.json").read()))

                    RequestFilter.dispatch(request)

                    call_list = get_original_app_mock.call_args_list
                    for effective_call in call_list:
                        self.assertEqual(mock.call(ctx_mock), effective_call, "Alguma chamada nao passou ctx para self.get_original_all()")
            except Exception as e:
                import traceback
                traceback.print_exc()
                self.fail("Nao deveria ter dado exception, %s" % e)

    def test_app_with_one_filter_disabled(self):
        one_filter_disabled_app = {
            "id": "/foo",
            "env": {
                "ENV_A ": "   VALUE A   ",
            },
            "container": {
                "docker": {
                    "image": "alpine",
                    "network": "BRIDGE",
                }
            },
            "labels": {   
                "hollowman.filter.trim.disable": "true" 
            }
        }
        with application.test_request_context(
                '/v2/apps/foo/restart',
                data=json.dumps(one_filter_disabled_app),
                content_type="application/json"):
            with mock.patch.object(hollowman.filters.BaseFilter, "get_original_app") as get_original_app_mock: #, \
                get_original_app_mock.return_value = MarathonApp(**one_filter_disabled_app)

                modified_request = RequestFilter.dispatch(request)

                self.assertTrue("ENV_A " in modified_request.get_json()['env'].keys(), "Fitlro Trim não deveria ter rodado")
                self.assertEqual("   VALUE A   ", modified_request.get_json()['env']['ENV_A '], "Filtro <trim> não deveria ter rodado")

    def test_app_with_one_filter_disabled_incomplete_body_no_label_modification(self):
        """
        Quando há modificações em labels, o marathon UI manda a key "labels" no request.
        Se essa key **não está presente** significa que o que deve valer é o que está na app original
        """
        one_filter_disabled_app = {
            "id": "/foo",
            "env": {
                "ENV_A ": "   VALUE A   ",
            },
            "container": {
                "docker": {
                    "image": "alpine",
                    "network": "BRIDGE",
                }
            },
            "labels": {   
                "hollowman.filter.trim.disable": "true"
            }
        }
        with application.test_request_context(
                '/v2/apps/foo/restart',
                data=json.dumps({"instances": 1}),
                content_type="application/json"):
            with mock.patch.object(hollowman.filters.BaseFilter, "get_original_app") as get_original_app_mock: #, \
                get_original_app_mock.return_value = MarathonApp(**one_filter_disabled_app)

                modified_request = RequestFilter.dispatch(request)

                self.assertTrue("ENV_A " in modified_request.get_json()['env'].keys(), "Fitlro <trim> não deveria ter rodado")
                self.assertEqual("   VALUE A   ", modified_request.get_json()['env']['ENV_A '], "Filtro <trim> não deveria ter rodado")

    def test_app_with_one_filter_disabled_incomplete_body_with_label_modification(self):
        """
        Quando há modificações em labels, o marathon UI manda a key "labels" no request.
        Nesse caso devemos rodar o filtro mesmo que a app original possua a label de disable
        """
        one_filter_disabled_app = {
            "id": "/foo",
            "container": {
                "docker": {
                    "image": "alpine",
                    "network": "BRIDGE",
                    "forcePullImage": True
                }
            },
            "labels": {   
                "hollowman.filter.pull.disable": "true"
            }
        }
        request_app = one_filter_disabled_app.copy()
        request_app['labels'] = {"my-other-label": "my-label-value"}
        request_app['container']['docker']['forcePullImage'] = False

        with application.test_request_context(
                '/v2/apps/foo/restart',
                data=json.dumps(request_app),
                content_type="application/json"):
            with mock.patch.object(hollowman.filters.BaseFilter, "get_original_app") as get_original_app_mock: #, \
                get_original_app_mock.return_value = MarathonApp(**one_filter_disabled_app)

                modified_request = RequestFilter.dispatch(request)

                self.assertTrue(modified_request.get_json()['container']['docker']['forcePullImage'], "Fitlro <pull> deveria ter rodado")

    def test_app_with_more_than_one_filter_disabled(self):
        one_filter_disabled_app = {
            "id": "/foo",
            "env": {
                "ENV_A ": "   VALUE A   ",
            },
            "container": {
                "docker": {
                    "image": "alpine",
                    "network": "BRIDGE",
                    "forcePullImage": False,
                }
            },
            "labels": {   
                "hollowman.filter.trim.disable": "true",
                "hollowman.filter.pull.disable": "true" 
            }
        }
        with application.test_request_context(
                '/v2/apps/foo/restart',
                data=json.dumps(one_filter_disabled_app),
                content_type="application/json"):
            with mock.patch.object(hollowman.filters.BaseFilter, "get_original_app") as get_original_app_mock: #, \
                get_original_app_mock.return_value = MarathonApp(**one_filter_disabled_app)

                modified_request = RequestFilter.dispatch(request)

                self.assertTrue("ENV_A " in modified_request.get_json()['env'].keys(), "Fitlro Trim não deveria ter rodado")
                self.assertEqual("   VALUE A   ", modified_request.get_json()['env']['ENV_A '], "Filtro <trim> não deveria ter rodado")
                self.assertFalse(modified_request.get_json()['container']['docker']['forcePullImage'])

    def test_app_enabling_filter(self):
        """
        Se a app que já está gravada no Marathon 
        tem a label que desabilita um filtro, mas a app do payload do request **não tem** essa label,
        o filtro deve ser incluído no dispatch atual!

        Se ele não for, o usuário terá que salvar a app duas vezes para que o filtro rode.
        Ex:
            App atualmente está com label=hollowman.filter.trim.disable=true;
            User salva a app sem essa label;

            Se o filtro nao for incluido no momento desse "save" a app vai ser salva apenas sem a label e os DNS default
            **não serão** adicionados. Para que essa app receba os DNSs uma *nova* modificação deverá ser feita.

            Por isso temos que incluir o filtro no momento em que uma app está sendo salva sem a label de disable.
        """
        base_app = {
            "id": "/foo",
            "env": {
                "ENV_A  ": "VALUE A  ",
            },
            "container": {
                "docker": {
                    "image": "alpine",
                    "network": "BRIDGE",
                    "forcePullImage": False,
                }
            },

        }

        original_app = base_app.copy()
        original_app.update({
            "labels": {   
                "hollowman.filter.trim.disable": "true",
            }
        })
        request_app = base_app.copy()
        request_app['env']['NEW ENV  '] = 'NEW VALUE  '
        request_app['labels'] = {}

        with application.test_request_context(
                '/v2/apps/foo/',
                data=json.dumps(request_app),
                method="PUT",
                content_type="application/json"):
            with mock.patch.object(hollowman.filters.BaseFilter, "get_original_app") as get_original_app_mock: #, \
                get_original_app_mock.return_value = MarathonApp(**original_app)

                modified_request = RequestFilter.dispatch(request)

                self.assertEqual(2, len(modified_request.get_json()['env'].keys()))
                self.assertTrue("ENV_A  " not in modified_request.get_json()['env'].keys(), "Fitlro <trim> deveria ter rodado")
                self.assertEqual("VALUE A", modified_request.get_json()['env']['ENV_A'], "Filtro <trim> deveria ter rodado")
                self.assertEqual("NEW VALUE", modified_request.get_json()['env']['NEW ENV'])

    def test_app_disabling_filter(self):
        """
        Análogo ao disabling.

        Se a versao da app que está no marathon não tem a label, mas o payload está chegando com a label de disable,
        o filtro *não* deve ser incluído no momento desse save.
        """
        base_app = {
            "id": "/foo",
            "env": {
                "ENV_A": "VALUE A",
            },
            "container": {
                "docker": {
                    "image": "alpine",
                    "network": "BRIDGE",
                    "forcePullImage": False,
                }
            },

        }

        original_app = base_app.copy()

        request_app = base_app.copy()
        request_app.update({
            "labels": {   
                "hollowman.filter.trim.disable": "true",
            }
        })
        request_app['env']['NEW ENV  '] = 'NEW VALUE  '

        with application.test_request_context(
                '/v2/apps/foo/',
                data=json.dumps(request_app),
                method="PUT",
                content_type="application/json"):
            with mock.patch.object(hollowman.filters.BaseFilter, "get_original_app") as get_original_app_mock: #, \
                get_original_app_mock.return_value = MarathonApp(**original_app)
                #import ipdb; ipdb.set_trace()
                modified_request = RequestFilter.dispatch(request)

                self.assertTrue("ENV_A" in modified_request.get_json()['env'].keys(), "Env original não deveria ter sido modificada")
                self.assertEqual("VALUE A", modified_request.get_json()['env']['ENV_A'], "Env original não deveria ter sido modificada")
                self.assertEqual("NEW VALUE  ", modified_request.get_json()['env']['NEW ENV  '], "Fitlro <trim> rodou, não deveria")

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
