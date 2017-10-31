
import json
from flask import Response as FlaskResponse
from marathon.models.group import MarathonGroup
from responses import RequestsMock


import unittest
from http import HTTPStatus
from copy import deepcopy


from hollowman import conf
from hollowman.http_wrappers.response import Response
from hollowman.models import User, Account
from hollowman.app import application
from hollowman.dispatcher import dispatch_response_pipeline
from tests.utils import with_json_fixture


class DummyFilter:
    def response_group(self, user, response_group, original_group):
        response_group.id = "/dummy" + response_group.id
        for app in response_group.apps:
            app.id = "/dummy" + app.id
        return response_group

class FooFilter:
    def response_group(self, user, response_group, original_group):
        for app in response_group.apps:
            app.id = "/foo" + app.id
        return response_group


class ResponsePipelineTest(unittest.TestCase):

    def setUp(self):
        self.user = User(tx_email="user@host.com.br")
        self.account = Account(name="Dev Account", namespace="dev", owner="company")
        self.user.current_account = self.account

    @with_json_fixture("../fixtures/group_dev_namespace_with_apps.json")
    def test_call_filter_method_passing_each_group(self, group_dev_namespace_fixture):
        """
        Todos os grupos de um response devem ser passados para os filtros,
        um de cada vez
        """

        with application.test_request_context("/v2/groups/group-b", method="GET") as ctx:
            ctx.request.user = self.user
            ok_response = FlaskResponse(
                response=json.dumps(group_dev_namespace_fixture['groups'][1]),
                status=HTTPStatus.OK,
                headers={}
            )
            with RequestsMock() as rsps:
                rsps.add(method='GET', url=conf.MARATHON_ENDPOINT + '/v2/groups//dev/group-b',
                         body=json.dumps(deepcopy(group_dev_namespace_fixture['groups'][1])), status=200)
                rsps.add(method='GET', url=conf.MARATHON_ENDPOINT + '/v2/groups//dev/group-b/group-b0',
                         body=json.dumps(deepcopy(group_dev_namespace_fixture['groups'][1]['groups'][0])), status=200)

                response_wrapper = Response(ctx.request, ok_response)
                final_response = dispatch_response_pipeline(user=self.user,
                                                            response=response_wrapper,
                                                            filters_pipeline=[DummyFilter()])
                final_response_data = json.loads(final_response.data)
                returned_group = MarathonGroup.from_json(final_response_data)
                self.assertEqual("/dummy/dev/group-b", returned_group.id)
                self.assertEqual("/dummy/dev/group-b/group-b0", returned_group.groups[0].id)


    @with_json_fixture("../fixtures/group_dev_namespace_with_apps.json")
    def test_filters_can_modifi_all_apps_from_group_and_subgroups(self, group_dev_namespace_fixture):
        """
        Um fltro deve poder alterar todas as apps de todos os grupos de um response.
        """
        with application.test_request_context("/v2/groups/group-b", method="GET") as ctx:
            ctx.request.user = self.user
            ok_response = FlaskResponse(
                response=json.dumps(group_dev_namespace_fixture['groups'][1]),
                status=HTTPStatus.OK,
                headers={}
            )
            with RequestsMock() as rsps:
                rsps.add(method='GET', url=conf.MARATHON_ENDPOINT + '/v2/groups//dev/group-b',
                         body=json.dumps(deepcopy(group_dev_namespace_fixture['groups'][1])), status=200)
                rsps.add(method='GET', url=conf.MARATHON_ENDPOINT + '/v2/groups//dev/group-b/group-b0',
                         body=json.dumps(deepcopy(group_dev_namespace_fixture['groups'][1]['groups'][0])), status=200)

                response_wrapper = Response(ctx.request, ok_response)
                final_response = dispatch_response_pipeline(user=self.user,
                                                            response=response_wrapper,
                                                            filters_pipeline=[DummyFilter()])
                final_response_data = json.loads(final_response.data)
                returned_group = MarathonGroup.from_json(final_response_data)
                self.assertEqual("/dummy/dev/group-b/appb0", returned_group.apps[0].id)
                self.assertEqual("/dummy/dev/group-b/group-b0/app0", returned_group.groups[0].apps[0].id)

    @with_json_fixture("../fixtures/group_dev_namespace_with_apps.json")
    def test_changes_from_all_filters_are_persisted_after_response_join(self, group_dev_namespace_fixture):
        """
        Certificamos que uma modificação de um filtro não é perdida durante a
        execução do pipeline. No response final, todas as modificações devem estar
        disponíveis.
        """
        with application.test_request_context("/v2/groups/group-b", method="GET") as ctx:
            ctx.request.user = self.user
            ok_response = FlaskResponse(
                response=json.dumps(group_dev_namespace_fixture['groups'][1]),
                status=HTTPStatus.OK,
                headers={}
            )
            with RequestsMock() as rsps:
                rsps.add(method='GET', url=conf.MARATHON_ENDPOINT + '/v2/groups//dev/group-b',
                         body=json.dumps(deepcopy(group_dev_namespace_fixture['groups'][1])), status=200)
                rsps.add(method='GET', url=conf.MARATHON_ENDPOINT + '/v2/groups//dev/group-b/group-b0',
                         body=json.dumps(deepcopy(group_dev_namespace_fixture['groups'][1]['groups'][0])), status=200)

                response_wrapper = Response(ctx.request, ok_response)
                final_response = dispatch_response_pipeline(user=self.user,
                                                            response=response_wrapper,
                                                            filters_pipeline=[DummyFilter(), FooFilter()])
                final_response_data = json.loads(final_response.data)
                returned_group = MarathonGroup.from_json(final_response_data)
                self.assertEqual("/foo/dummy/dev/group-b/appb0", returned_group.apps[0].id)
                self.assertEqual("/foo/dummy/dev/group-b/group-b0/app0", returned_group.groups[0].apps[0].id)


    @unittest.skip("Temos que decidir se vamos retornar o group com minimal=True ou False")
    def test_an_empty_root_group_should_return_and_empty_group_definition(self):
        """
        A UI parece aceitar bem um representação de group sem alguns campos, o que é equivalente
        ao minimal=True.
        """
        self.fail()
