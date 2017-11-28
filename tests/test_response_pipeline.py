
from flask import Response as FlaskResponse
from copy import deepcopy
import unittest
import json
from responses import RequestsMock

from hollowman.app import application
from hollowman.http_wrappers.response import Response
from hollowman.dispatcher import dispatch_response_pipeline
from hollowman import conf
from hollowman.models import User, Account

from tests.utils import with_json_fixture


class RemoveNSFilter:
    def response(self, user, response_app, original_app):
        response_app.id = response_app.id.replace("/dev/", "/")
        return response_app


class ResponsePipelineTest(unittest.TestCase):

    @with_json_fixture("single_full_app.json")
    def setUp(self, single_full_app_fixture):
        self.single_full_app_fixture = single_full_app_fixture
        self.user = User(tx_name="User", tx_email="user@host.com")
        self.user.current_account = Account(name="Some Account", namespace="dev", owner="company")

    def test_response_has_app_modified_by_filter(self):
        """
        Certificamos que um request em uma app, roda o pipeline
        e essa app pode ser modificada por algum filtro
        """
        with application.test_request_context("/v2/apps/dev/foo", method="GET") as ctx:
            single_full_app_one = deepcopy(self.single_full_app_fixture)
            single_full_app_one['id'] = '/dev/foo'

            _url = conf.MARATHON_ENDPOINT + '/v2/apps//dev/foo'
            with RequestsMock() as rsps:
                rsps.add(method='GET',
                         url=_url,
                         json={'app': single_full_app_one},
                         status=200)
                original_response = FlaskResponse(response=json.dumps({'app': single_full_app_one}),
                                                  status=200,
                                                  headers={})

                response_wrapper = Response(ctx.request, original_response)
                final_response = dispatch_response_pipeline(user=self.user,
                                                            response=response_wrapper,
                                                           filters_pipeline=(RemoveNSFilter(),))
                self.assertEqual(200, final_response.status_code)
                self.assertEqual("/foo", json.loads(final_response.data)['app']['id'])


    def test_response_has_list_of_apps_modified_by_filters(self):
        """
        Certificamos que uma lista de apps pode ser modificada por algum
        filtro de response.
        """
        with application.test_request_context("/v2/apps/", method="GET") as ctx:
            single_full_app_one = deepcopy(self.single_full_app_fixture)
            single_full_app_one['id'] = '/dev/foo'

            single_full_app_two = deepcopy(self.single_full_app_fixture)
            single_full_app_two['id'] = '/dev/other-app'

            with RequestsMock() as rsps:
                rsps.add(method='GET', url=conf.MARATHON_ENDPOINT + '/v2/apps//dev/foo',
                         body=json.dumps({'app': single_full_app_one}), status=200)
                rsps.add(method='GET', url=conf.MARATHON_ENDPOINT + '/v2/apps//dev/other-app',
                         body=json.dumps({'app': single_full_app_two}), status=200)

                original_response = FlaskResponse(response=json.dumps({'apps': [single_full_app_one, single_full_app_two]}),
                                                  status=200, headers={})

                response_wrapper = Response(ctx.request, original_response)
                final_response = dispatch_response_pipeline(user=self.user,
                                                            response=response_wrapper,
                                                           filters_pipeline=(RemoveNSFilter(),))
                response_data = json.loads(final_response.data)
                self.assertEqual(200, final_response.status_code)
                self.assertEqual(2, len(response_data['apps']))
                self.assertEqual("/foo", response_data['apps'][0]['id'])
                self.assertEqual("/other-app", response_data['apps'][1]['id'])

    def test_remove_from_response_apps_outside_current_namespace(self):
        with application.test_request_context("/v2/apps/", method="GET") as ctx:
            single_full_app_one = deepcopy(self.single_full_app_fixture)
            single_full_app_one['id'] = '/dev/foo'

            single_full_app_two = deepcopy(self.single_full_app_fixture)
            single_full_app_two['id'] = '/dev/other-app'

            single_full_app_three = deepcopy(self.single_full_app_fixture)
            single_full_app_three['id'] = '/othernamespace/other-app'

            with RequestsMock() as rsps:
                rsps.add(method='GET', url=conf.MARATHON_ENDPOINT + '/v2/apps//dev/foo',
                         body=json.dumps({'app': single_full_app_one}), status=200)
                rsps.add(method='GET', url=conf.MARATHON_ENDPOINT + '/v2/apps//dev/other-app',
                         body=json.dumps({'app': single_full_app_two}), status=200)
                rsps.add(method='GET', url=conf.MARATHON_ENDPOINT + '/v2/apps//othernamespace/other-app',
                         body=json.dumps({'app': single_full_app_three}), status=200)

                original_response = FlaskResponse(response=json.dumps({'apps': [single_full_app_one, single_full_app_two, single_full_app_three]}),
                                                  status=200, headers={})

                response_wrapper = Response(ctx.request, original_response)
                final_response = dispatch_response_pipeline(user=self.user,
                                                            response=response_wrapper,
                                                           filters_pipeline=(RemoveNSFilter(),))
                response_data = json.loads(final_response.data)
                self.assertEqual(200, final_response.status_code)
                self.assertEqual(2, len(response_data['apps']))
                self.assertEqual("/foo", response_data['apps'][0]['id'])
                self.assertEqual("/other-app", response_data['apps'][1]['id'])

    def test_do_not_call_filter_if_it_doesnt_implement_response_method(self):
        class DummyRequestFilter:
            def write(self, user, request_app, original_app):
                return request_app

        with application.test_request_context("/v2/apps/foo", method="GET") as ctx:
            single_full_app_one = deepcopy(self.single_full_app_fixture)
            single_full_app_one['id'] = "/dev/foo"

            with RequestsMock() as rsps:
                rsps.add(method='GET', url=conf.MARATHON_ENDPOINT + '/v2/apps//foo',
                         json={"app": single_full_app_one}, status=200)

                original_response = FlaskResponse(response=json.dumps({"app": single_full_app_one}),
                                                  status=200, headers={})

                response_wrapper = Response(ctx.request, original_response)
                final_response = dispatch_response_pipeline(user=self.user,
                                                            response=response_wrapper,
                                                            filters_pipeline=[DummyRequestFilter()])
                response_data = json.loads(final_response.data)
                self.assertEqual(200, final_response.status_code)
                self.assertEqual("/dev/foo", response_data['app']['id'])

    @with_json_fixture("../fixtures/tasks/get_single_infra_namespace.json")
    def test_response_task_returns_empty_response_when_all_tasks_are_from_other_namespace(self, tasks_namespace_infra_fixture):
        with application.test_request_context("/v2/tasks/", method="GET") as ctx:

            original_response = FlaskResponse(response=json.dumps(tasks_namespace_infra_fixture),
                                              status=200)

            response_wrapper = Response(ctx.request, original_response)
            final_response = dispatch_response_pipeline(user=self.user,
                                                        response=response_wrapper,
                                                        filters_pipeline=[])
            response_data = json.loads(final_response.data)
            self.assertEqual(200, final_response.status_code)
            self.assertEqual(0, len(response_data['tasks']))

    @with_json_fixture("../fixtures/tasks/get_single_namespace.json")
    def test_response_task_filter_modifies_task(self, tasks_get_fixture):
        class ModifyTaskFilter:
            def response_task(self, user, response_task, original_task):
                response_task.id = f"{response_task.id}_bla"
                return response_task

        with application.test_request_context("/v2/tasks/", method="GET") as ctx:

            original_response = FlaskResponse(response=json.dumps(tasks_get_fixture),
                                              status=200)

            response_wrapper = Response(ctx.request, original_response)
            final_response = dispatch_response_pipeline(user=self.user,
                                                        response=response_wrapper,
                                                        filters_pipeline=[ModifyTaskFilter()])
            response_data = json.loads(final_response.data)
            self.assertEqual(200, final_response.status_code)
            self.assertEqual(3, len(response_data['tasks']))
            self.assertEqual([
                "dev_waiting.01339ffa-ce9c-11e7-8144-2a27410e5638_bla",
                "dev_waiting.0432fd4b-ce9c-11e7-8144-2a27410e5638_bla",
                "dev_waiting.75b2ed9c-ce9c-11e7-8144-2a27410e5638_bla"
            ], [task['id'] for task in response_data['tasks']])

    @with_json_fixture("../fixtures/tasks/get_multi_namespace.json")
    def test_response_task_remove_from_response_tasks_outside_namespace(self, tasks_multinamespace_fixure):
        class ModifyTaskFilter:
            def response_task(self, user, response_task, original_task):
                response_task.id = response_task.id.replace(f"{user.current_account.namespace}_", "")
                return response_task

        with application.test_request_context("/v2/tasks/", method="GET") as ctx:

            original_response = FlaskResponse(response=json.dumps(tasks_multinamespace_fixure),
                                              status=200)

            response_wrapper = Response(ctx.request, original_response)
            final_response = dispatch_response_pipeline(user=self.user,
                                                        response=response_wrapper,
                                                        filters_pipeline=[ModifyTaskFilter()])
            response_data = json.loads(final_response.data)
            self.assertEqual(200, final_response.status_code)
            self.assertEqual(2, len(response_data['tasks']))
            self.assertEqual([
                "waiting.01339ffa-ce9c-11e7-8144-2a27410e5638",
                "waiting.0432fd4b-ce9c-11e7-8144-2a27410e5638",
            ], [task['id'] for task in response_data['tasks']])

    @with_json_fixture("../fixtures/tasks/get_multi_namespace.json")
    def test_response_task_remove_from_response_tasks_outside_same_prefix_namespace(self, tasks_multinamespace_fixure):
        """
        Confirmamos que uma task do namespace "developers" *deve ser removida* quando o usuário faz parte
        do namespace "dev", mesmo esses dois namespaces começando pelo mesmo prefixo
        """
        with application.test_request_context("/v2/tasks/", method="GET") as ctx:

            original_response = FlaskResponse(response=json.dumps(tasks_multinamespace_fixure),
                                              status=200)

            response_wrapper = Response(ctx.request, original_response)
            final_response = dispatch_response_pipeline(user=self.user,
                                                        response=response_wrapper,
                                                        filters_pipeline=[])
            response_data = json.loads(final_response.data)
            self.assertEqual(200, final_response.status_code)
            self.assertEqual([
                "dev_waiting.01339ffa-ce9c-11e7-8144-2a27410e5638",
                "dev_waiting.0432fd4b-ce9c-11e7-8144-2a27410e5638",
            ], [task['id'] for task in response_data['tasks']])
            self.assertEqual(2, len(response_data['tasks']))

    @with_json_fixture("../fixtures/tasks/post?scale=true.json")
    def test_response_task_do_not_dispatch_pipeline_if_response_is_deployment(self, tasks_post_fixture):
        """
        Se o request for de escrita em /v2/tasks e foi passado `?scale=true`, não devemos
        rodar o pipeline, já que nesse response tem apenas um DeploymentId
        """
        with application.test_request_context("/v2/tasks/delete?scale=true", method="POST") as ctx:

            original_response = FlaskResponse(response=json.dumps(tasks_post_fixture),
                                              status=200)

            response_wrapper = Response(ctx.request, original_response)
            final_response = dispatch_response_pipeline(user=self.user,
                                                        response=response_wrapper,
                                                        filters_pipeline=[])
            response_data = json.loads(final_response.data)
            self.assertEqual(200, final_response.status_code)
            self.assertEqual("5ed4c0c5-9ff8-4a6f-a0cd-f57f59a34b43", response_data['deploymentId'])

