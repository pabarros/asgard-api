

import unittest
import json
from itertools import chain

from flask import Response as FlaskResponse
from marathon.models import MarathonDeployment
from marathon.models.group import MarathonGroup
from marathon.models.task import MarathonTask 

from http import HTTPStatus


from hollowman.app import application
from hollowman.models import Account, User
from hollowman.marathonapp import SieveMarathonApp
from hollowman.filters.namespace import NameSpaceFilter
from hollowman.http_wrappers.response import Response
from tests.utils import with_json_fixture

class TestNamespaceFilter(unittest.TestCase):

    @with_json_fixture("single_full_app.json")
    def setUp(self, single_full_app_fixture):
        self.filter = NameSpaceFilter()
        self.request_app = SieveMarathonApp.from_json(single_full_app_fixture)
        self.original_app = SieveMarathonApp.from_json(single_full_app_fixture)
        self.account = Account(name="Dev Account", namespace="dev", owner="company")
        self.user = User(tx_email="user@host.com.br")
        self.user.current_account = self.account

    def test_add_namespace_original_app_already_have_namespace(self):
        self.original_app.id = "/dev/foo"
        modified_app = self.filter.write(self.user, self.request_app, self.original_app)
        self.assertEqual("/dev/foo", modified_app.id)

    def test_add_namespace_request_app_already_have_namespace(self):
        """
        Independente de qualquer coisa, temos *sempre* que adicionar
        o namespace ao wrapped_request app. Isso evita que alguém consiga acessar
        uma app de outro namespace.
        """
        self.original_app.id = "/dev/foo"
        self.request_app.id = "/dev/foo"
        modified_app = self.filter.write(self.user, self.request_app, self.original_app)
        self.assertEqual("/dev/dev/foo", modified_app.id)

    def test_add_namespace_create_new_app(self):
        """
        Para novas apps, sempre vamos adicionar o prefixo.
        """
        modified_app = self.filter.write(self.user, self.request_app, SieveMarathonApp())
        self.assertEqual("/dev/foo", modified_app.id)

    @with_json_fixture("../fixtures/tasks/get.json")
    def test_request_add_namespace_to_all_tasks(self, tasks_get_fixture):
        """
        Um POST em /v2/tasks/delete deve ajustar o ID de todas as tasks
        envolvidas
        """
        task = MarathonTask.from_json(tasks_get_fixture['tasks'][0])
        filtered_task  = self.filter.write(self.user, task, task)
        self.assertEqual("dev_waiting.01339ffa-ce9c-11e7-8144-2a27410e5638", filtered_task.id)
        self.assertEqual("/dev/waiting", filtered_task.app_id)

    def test_does_nothing_if_user_is_none(self):
        modified_app = self.filter.write(None, self.request_app, SieveMarathonApp())
        self.assertEqual("/foo", modified_app.id)

    @with_json_fixture("../fixtures/single_full_app_with_tasks.json")
    def test_response_apps_remove_namespace_from_all_tasks(self, single_full_app_with_tasks_fixture):
        request_app = original_app = SieveMarathonApp.from_json(single_full_app_with_tasks_fixture)

        self.assertEqual(3, len(request_app.tasks))
        modified_app = self.filter.response(self.user, request_app, original_app)
        self.assertEqual("foo.a29b3666-be63-11e7-8ef1-0242a8c1e33e", modified_app.tasks[0].id)
        self.assertEqual("/foo", modified_app.tasks[0].app_id)

        self.assertEqual("foo.a31e220e-be63-11e7-8ef1-0242a8c1e33e", modified_app.tasks[1].id)
        self.assertEqual("/foo", modified_app.tasks[1].app_id)

        self.assertEqual("foo.a31dfafb-be63-11e7-8ef1-0242a8c1e33e", modified_app.tasks[2].id)
        self.assertEqual("/foo", modified_app.tasks[2].app_id)

    @with_json_fixture("../fixtures/single_full_app_with_tasks.json")
    def test_response_apps_remove_namespace_from_all_tasks_empty_task_list(self, single_full_app_with_tasks_fixture):
        request_app = original_app = SieveMarathonApp.from_json(single_full_app_with_tasks_fixture)
        request_app.id = "/dev/foo"
        request_app.tasks = []
        original_app.id = "/dev/foo"
        original_app.tasks = []
        self.assertEqual(0, len(request_app.tasks))

        modified_app = self.filter.response(self.user, request_app, original_app)
        self.assertEqual(0, len(self.request_app.tasks))

    def test_response_apps__remove_namespace_if_original_app_already_have_namespace(self):
        self.original_app.id = "/dev/foo"
        modified_app = self.filter.response(self.user, self.request_app, self.original_app)
        self.assertEqual("/foo", modified_app.id)

    def test_response_apps_does_nothing_if_user_is_none(self):
        self.request_app.id = "/dev/foo"
        modified_app = self.filter.response(None, self.request_app, SieveMarathonApp())
        self.assertEqual("/dev/foo", modified_app.id)

    def test_remove_namspace_from_string(self):
        self.assertEqual("/", self.filter._remove_namespace(self.user, "/dev"))
        self.assertEqual("/", self.filter._remove_namespace(self.user, "/dev/"))
        self.assertEqual("/foo/bar", self.filter._remove_namespace(self.user, "/dev/foo/bar"))
        self.assertEqual("/infra/foo", self.filter._remove_namespace(self.user, "/infra/foo"))
        self.assertEqual("/", self.filter._remove_namespace(self.user, "/"))

    @with_json_fixture("../fixtures/group_dev_namespace_with_apps.json")
    def test_response_group_remove_namespace_from_group_name(self, group_dev_namespace_fixture):
        with application.test_request_context("/v2/groups/group-b", method="GET") as ctx:
            ctx.request.user = self.user
            ok_response = FlaskResponse(
                response=json.dumps(group_dev_namespace_fixture['groups'][1]),
                status=HTTPStatus.OK,
                headers={}
            )
            response_group = original_group = MarathonGroup.from_json(group_dev_namespace_fixture['groups'][1])
            response_wrapper = Response(ctx.request, ok_response)
            filtered_group = self.filter.response_group(self.user, response_group, original_group)
            self.assertEqual("/group-b", filtered_group.id)
            self.assertEqual(1, len(filtered_group.groups))
            # Não removemos o namespace de subgrupos.
            self.assertEqual("/dev/group-b/group-b0", filtered_group.groups[0].id)

    @with_json_fixture("../fixtures/group_dev_namespace_with_apps.json")
    def test_response_group_remove_namespace_from_app_name(self, group_dev_namespace_fixture):
        """
        Devemos remover o namespace de todas as apps to grupo.
        Mas não das apps dos subgrupos
        """
        with application.test_request_context("/v2/groups/group-b", method="GET") as ctx:
            ctx.request.user = self.user
            ok_response = FlaskResponse(
                response=json.dumps(group_dev_namespace_fixture['groups'][1]),
                status=HTTPStatus.OK,
                headers={}
            )
            response_group = original_group = MarathonGroup.from_json(group_dev_namespace_fixture['groups'][1])
            response_wrapper = Response(ctx.request, ok_response)
            filtered_group = self.filter.response_group(self.user, response_group, original_group)
            self.assertEqual("/group-b", filtered_group.id)
            self.assertEqual(1, len(filtered_group.apps))
            self.assertEqual("/group-b/appb0", filtered_group.apps[0].id)

    @with_json_fixture("../fixtures/group_dev_namespace_with_apps_with_tasks.json")
    def test_response_group_remove_namespace_from_all_tasks_of_all_apps(self, group_dev_namespace_fixture):
        with application.test_request_context("/v2/groups/a", method="GET") as ctx:
            ctx.request.user = self.user
            ok_response = FlaskResponse(
                response=json.dumps(group_dev_namespace_fixture['groups'][0]),
                status=HTTPStatus.OK,
                headers={}
            )
            response_group = original_group = MarathonGroup.from_json(group_dev_namespace_fixture['groups'][0])
            response_wrapper = Response(ctx.request, ok_response)
            filtered_group = self.filter.response_group(self.user, response_group, original_group)
            self.assertEqual(1, len(filtered_group.apps))

            self.assertEqual("a_app0.a31dfafb-be63-11e7-8ef1-0242a8c1e33e", filtered_group.apps[0].tasks[0].id)
            self.assertEqual("/a/app0", filtered_group.apps[0].tasks[0].app_id)

            self.assertEqual("a_app0.a31dfafb-be63-11e7-8ef1-0242a8c1e44o", filtered_group.apps[0].tasks[1].id)
            self.assertEqual("/a/app0", filtered_group.apps[0].tasks[1].app_id)


    @with_json_fixture("../fixtures/group_dev_namespace_with_apps_with_tasks.json")
    def test_response_group_remove_namespace_from_all_tasks_of_all_apps_empty_task_list(self, group_dev_namespace_fixture):
        with application.test_request_context("/v2/groups/a", method="GET") as ctx:
            ctx.request.user = self.user
            ok_response = FlaskResponse(
                response=json.dumps(group_dev_namespace_fixture['groups'][0]),
                status=HTTPStatus.OK,
                headers={}
            )
            response_group = original_group = MarathonGroup.from_json(group_dev_namespace_fixture['groups'][0])
            response_group.apps[0].tasks = []
            original_group.apps[0].tasks = []
            response_wrapper = Response(ctx.request, ok_response)
            filtered_group = self.filter.response_group(self.user, response_group, original_group)
            self.assertEqual(1, len(filtered_group.apps))
            self.assertEqual(0, len(filtered_group.apps[0].tasks))

    @with_json_fixture("deployments/get.json")
    def test_response_deployments_remove_namespace_from_all_app_ids(self, fixture):
        deployment = MarathonDeployment.from_json(fixture[0])
        self.filter.response_deployment(self.user, deployment)

        self.assertEqual(deployment.affected_apps, ['/foo'])

        current_action_apps = [action.app for action in deployment.current_actions]
        self.assertEqual(current_action_apps, ['/foo'])

        actions = [step.actions for step in deployment.steps]
        step_apps = [action.app for action in  chain.from_iterable(actions)]
        self.assertEqual(step_apps, ['/foo', '/foo'])

    @with_json_fixture("../fixtures/tasks/get.json")
    def test_response_tasks_remove_namespace_from_all_tasks(self, tasks_get_fixture):
        task =  MarathonTask.from_json(tasks_get_fixture['tasks'][0])
        task.id = "dev_" + task.id
        task.app_id = "/dev" + task.app_id
        filtered_task = self.filter.response_task(self.user, task, task)
        self.assertEqual("waiting.01339ffa-ce9c-11e7-8144-2a27410e5638", filtered_task.id)
        self.assertEqual("/waiting", filtered_task.app_id)

