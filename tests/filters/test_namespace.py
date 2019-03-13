import json
import unittest
from http import HTTPStatus
from itertools import chain

from flask import Response as FlaskResponse
from marathon.models import MarathonDeployment
from marathon.models.group import MarathonGroup
from marathon.models.queue import MarathonQueueItem
from marathon.models.task import MarathonTask

from hollowman.app import application
from hollowman.filters.namespace import NameSpaceFilter
from hollowman.http_wrappers.response import Response
from hollowman.marathonapp import AsgardApp
from hollowman.models import Account, User
from tests.utils import with_json_fixture


class TestNamespaceFilter(unittest.TestCase):
    @with_json_fixture("single_full_app.json")
    def setUp(self, single_full_app_fixture):
        self.filter = NameSpaceFilter()
        self.request_app = AsgardApp.from_json(single_full_app_fixture)
        self.original_app = AsgardApp.from_json(single_full_app_fixture)
        self.account = Account(
            name="Dev Account", namespace="dev", owner="company"
        )
        self.user = User(tx_email="user@host.com.br")
        self.user.current_account = self.account

    def test_add_namespace_original_app_already_have_namespace(self):
        self.original_app.id = "/dev/foo"
        modified_app = self.filter.write(
            self.user, self.request_app, self.original_app
        )
        self.assertEqual("/dev/foo", modified_app.id)

    def test_add_namespace_request_app_already_have_namespace(self):
        """
        Independente de qualquer coisa, temos *sempre* que adicionar
        o namespace ao wrapped_request app. Isso evita que alguém consiga acessar
        uma app de outro namespace.
        """
        self.original_app.id = "/dev/foo"
        self.request_app.id = "/dev/foo"
        modified_app = self.filter.write(
            self.user, self.request_app, self.original_app
        )
        self.assertEqual("/dev/dev/foo", modified_app.id)

    def test_add_namespace_create_new_app(self):
        """
        Para novas apps, sempre vamos adicionar o prefixo.
        """
        modified_app = self.filter.write(
            self.user, self.request_app, AsgardApp()
        )
        self.assertEqual("/dev/foo", modified_app.id)

    @with_json_fixture("../fixtures/tasks/get.json")
    def test_request_add_namespace_to_all_tasks(self, tasks_get_fixture):
        """
        Um POST em /v2/tasks/delete deve ajustar o ID de todas as tasks
        envolvidas
        """
        task = MarathonTask.from_json(tasks_get_fixture["tasks"][0])
        filtered_task = self.filter.write_task(self.user, task, task)
        self.assertEqual(
            "dev_waiting.01339ffa-ce9c-11e7-8144-2a27410e5638", filtered_task.id
        )
        self.assertEqual("/dev/waiting", filtered_task.app_id)

    @with_json_fixture("../fixtures/tasks/get.json")
    def test_request_add_namespace_to_all_tasks_empty_app_id(
        self, tasks_get_fixture
    ):
        """
        Um POST em /v2/tasks/delete deve ajustar o ID de todas as tasks
        envolvidas
        """
        task = MarathonTask.from_json(tasks_get_fixture["tasks"][0])
        task.app_id = None
        filtered_task = self.filter.write_task(self.user, task, task)
        self.assertEqual(
            "dev_waiting.01339ffa-ce9c-11e7-8144-2a27410e5638", filtered_task.id
        )
        self.assertIsNone(filtered_task.app_id)

    @with_json_fixture("../fixtures/single_full_app_with_tasks.json")
    def test_response_apps_remove_namespace_from_app_id_containig_namespace_in_its_name(
        self, single_full_app_with_tasks_fixture
    ):
        """
        Uma app com id = "/<namespace>/some/other/path/<namespace>/other/app" deve ter apenas a primeira ocorrência de "/<namespace>" removida.
        """
        response_app = original_app = AsgardApp.from_json(
            single_full_app_with_tasks_fixture
        )
        response_app.id = "/dev/some/other/path/dev/other/app"

        modified_app = self.filter.response(
            self.user, response_app, original_app
        )
        self.assertEqual("/some/other/path/dev/other/app", modified_app.id)

    @with_json_fixture("../fixtures/single_full_app_with_tasks.json")
    def test_response_apps_remove_namespace_from_all_tasks(
        self, single_full_app_with_tasks_fixture
    ):
        request_app = original_app = AsgardApp.from_json(
            single_full_app_with_tasks_fixture
        )

        self.assertEqual(3, len(request_app.tasks))
        modified_app = self.filter.response(
            self.user, request_app, original_app
        )
        self.assertEqual(
            "foo.a29b3666-be63-11e7-8ef1-0242a8c1e33e", modified_app.tasks[0].id
        )
        self.assertEqual("/foo", modified_app.tasks[0].app_id)

        self.assertEqual(
            "foo.a31e220e-be63-11e7-8ef1-0242a8c1e33e", modified_app.tasks[1].id
        )
        self.assertEqual("/foo", modified_app.tasks[1].app_id)

        self.assertEqual(
            "foo.a31dfafb-be63-11e7-8ef1-0242a8c1e33e", modified_app.tasks[2].id
        )
        self.assertEqual("/foo", modified_app.tasks[2].app_id)

        self.assertEqual(
            "foo.bb1f57d0-e755-11e8-9eac-0242eb39892d",
            modified_app.last_task_failure.task_id,
        )
        self.assertEqual("/foo", modified_app.last_task_failure.app_id)

    @with_json_fixture("../fixtures/single_full_app_with_tasks.json")
    def test_response_apps_remove_namespace_without_last_task_failure(
        self, single_full_app_with_tasks_fixture
    ):
        del single_full_app_with_tasks_fixture["lastTaskFailure"]
        request_app = original_app = AsgardApp.from_json(
            single_full_app_with_tasks_fixture
        )

        modified_app = self.filter.response(
            self.user, request_app, original_app
        )

        self.assertIsNone(modified_app.last_task_failure)

    @with_json_fixture("../fixtures/single_full_app_with_tasks.json")
    def test_response_apps_remove_namespace_from_all_tasks_empty_task_list(
        self, single_full_app_with_tasks_fixture
    ):
        request_app = original_app = AsgardApp.from_json(
            single_full_app_with_tasks_fixture
        )
        request_app.id = "/dev/foo"
        request_app.tasks = []
        original_app.id = "/dev/foo"
        original_app.tasks = []
        self.assertEqual(0, len(request_app.tasks))

        modified_app = self.filter.response(
            self.user, request_app, original_app
        )
        self.assertEqual(0, len(self.request_app.tasks))

    @with_json_fixture("../fixtures/single_full_app_with_tasks.json")
    def test_response_apps_returns_none_if_outside_current_namespace(
        self, single_full_app_with_tasks_fixture
    ):
        request_app = original_app = AsgardApp.from_json(
            single_full_app_with_tasks_fixture
        )
        request_app.id = original_app.id = "/othernamespace/foo"

        self.assertIsNone(
            self.filter.response(self.user, request_app, original_app)
        )

    def test_remove_namspace_from_app_or_group_id(self):
        self.assertEqual(
            "/",
            self.filter._remove_namespace(
                "/dev", self.user.current_account.namespace
            ),
        )
        self.assertEqual(
            "/",
            self.filter._remove_namespace(
                "/dev/", self.user.current_account.namespace
            ),
        )
        self.assertEqual(
            "/foo/bar",
            self.filter._remove_namespace(
                "/dev/foo/bar", self.user.current_account.namespace
            ),
        )
        self.assertEqual(
            "/infra/foo",
            self.filter._remove_namespace(
                "/infra/foo", self.user.current_account.namespace
            ),
        )
        self.assertEqual(
            "/",
            self.filter._remove_namespace(
                "/", self.user.current_account.namespace
            ),
        )

        # Apps que possuem o proprio namespace como parte de seu nome
        self.assertEqual(
            "/dev/myapp",
            self.filter._remove_namespace(
                "/dev/dev/myapp", self.user.current_account.namespace
            ),
        )
        self.assertEqual(
            "/myapp/dev/app",
            self.filter._remove_namespace(
                "/dev/myapp/dev/app", self.user.current_account.namespace
            ),
        )
        self.assertEqual(
            "/dev/myapp/dev/dev/app",
            self.filter._remove_namespace(
                "/dev/dev/myapp/dev/dev/app",
                self.user.current_account.namespace,
            ),
        )
        self.assertEqual(
            "/dev/myapp/dev",
            self.filter._remove_namespace(
                "/dev/dev/myapp/dev", self.user.current_account.namespace
            ),
        )
        self.assertEqual(
            "/dev",
            self.filter._remove_namespace(
                "/dev/dev", self.user.current_account.namespace
            ),
        )

    def test_remove_namespace_from_task(self):
        """
        Certifica que o namespace é removido corretamente, ou seja, apenas a primeira ocorrência deve
        ser removida
        """
        tasks = [
            MarathonTask.from_json(
                {
                    "id": "dev_app_my_other_dev_path",
                    "app_id": "/dev/app/my/other/dev/path",
                }
            )
        ]
        expected_task_ids = ["app_my_other_dev_path"]

        self.filter._remove_namespace_from_tasks(tasks, "dev")
        self.assertEqual(expected_task_ids, [task.id for task in tasks])

    @with_json_fixture("../fixtures/group_dev_namespace_with_apps.json")
    def test_response_group_remove_namespace_from_group_name(
        self, group_dev_namespace_fixture
    ):
        with application.test_request_context(
            "/v2/groups/group-b", method="GET"
        ) as ctx:
            ctx.request.user = self.user
            ok_response = FlaskResponse(
                response=json.dumps(group_dev_namespace_fixture["groups"][1]),
                status=HTTPStatus.OK,
                headers={},
            )
            response_group = original_group = MarathonGroup.from_json(
                group_dev_namespace_fixture["groups"][1]
            )
            original_group = original_group = MarathonGroup.from_json(
                group_dev_namespace_fixture["groups"][1]
            )
            response_wrapper = Response(ctx.request, ok_response)
            filtered_group = self.filter.response_group(
                self.user, response_group, original_group
            )
            self.assertEqual("/group-b", filtered_group.id)
            self.assertEqual(1, len(filtered_group.groups))
            # Não removemos o namespace de subgrupos.
            self.assertEqual(
                "/dev/group-b/group-b0", filtered_group.groups[0].id
            )

    @with_json_fixture("../fixtures/group_dev_namespace_with_apps.json")
    def test_response_group_remove_namespace_from_app_name(
        self, group_dev_namespace_fixture
    ):
        """
        Devemos remover o namespace de todas as apps to grupo.
        Mas não das apps dos subgrupos
        """
        with application.test_request_context(
            "/v2/groups/group-b", method="GET"
        ) as ctx:
            ctx.request.user = self.user
            ok_response = FlaskResponse(
                response=json.dumps(group_dev_namespace_fixture["groups"][1]),
                status=HTTPStatus.OK,
                headers={},
            )
            response_group = original_group = MarathonGroup.from_json(
                group_dev_namespace_fixture["groups"][1]
            )
            original_group = original_group = MarathonGroup.from_json(
                group_dev_namespace_fixture["groups"][1]
            )
            response_wrapper = Response(ctx.request, ok_response)
            filtered_group = self.filter.response_group(
                self.user, response_group, original_group
            )
            self.assertEqual("/group-b", filtered_group.id)
            self.assertEqual(1, len(filtered_group.apps))
            self.assertEqual("/group-b/appb0", filtered_group.apps[0].id)

    @with_json_fixture(
        "../fixtures/group_dev_namespace_with_apps_with_tasks.json"
    )
    def test_response_group_remove_namespace_from_all_tasks_of_all_apps(
        self, group_dev_namespace_fixture
    ):
        with application.test_request_context(
            "/v2/groups/a", method="GET"
        ) as ctx:
            ctx.request.user = self.user
            ok_response = FlaskResponse(
                response=json.dumps(group_dev_namespace_fixture["groups"][0]),
                status=HTTPStatus.OK,
                headers={},
            )
            response_group = original_group = MarathonGroup.from_json(
                group_dev_namespace_fixture["groups"][0]
            )
            response_wrapper = Response(ctx.request, ok_response)
            filtered_group = self.filter.response_group(
                self.user, response_group, original_group
            )
            self.assertEqual(1, len(filtered_group.apps))

            self.assertEqual(
                "a_app0.a31dfafb-be63-11e7-8ef1-0242a8c1e33e",
                filtered_group.apps[0].tasks[0].id,
            )
            self.assertEqual("/a/app0", filtered_group.apps[0].tasks[0].app_id)

            self.assertEqual(
                "a_app0.a31dfafb-be63-11e7-8ef1-0242a8c1e44o",
                filtered_group.apps[0].tasks[1].id,
            )
            self.assertEqual("/a/app0", filtered_group.apps[0].tasks[1].app_id)

    @with_json_fixture(
        "../fixtures/group_dev_namespace_with_apps_with_tasks.json"
    )
    def test_response_group_remove_namespace_from_all_tasks_of_all_apps_empty_task_list(
        self, group_dev_namespace_fixture
    ):
        with application.test_request_context(
            "/v2/groups/a", method="GET"
        ) as ctx:
            ctx.request.user = self.user
            ok_response = FlaskResponse(
                response=json.dumps(group_dev_namespace_fixture["groups"][0]),
                status=HTTPStatus.OK,
                headers={},
            )
            response_group = original_group = MarathonGroup.from_json(
                group_dev_namespace_fixture["groups"][0]
            )
            response_group.apps[0].tasks = []
            original_group.apps[0].tasks = []
            response_wrapper = Response(ctx.request, ok_response)
            filtered_group = self.filter.response_group(
                self.user, response_group, original_group
            )
            self.assertEqual(1, len(filtered_group.apps))

    @with_json_fixture("deployments/get.json")
    def test_response_deployments_return_none_if_outside_current_namespace(
        self, fixture
    ):
        deployment = MarathonDeployment.from_json(fixture[0])
        deployment.affected_apps = ["/othernamespace/foo"]
        self.assertIsNone(
            self.filter.response_deployment(self.user, deployment, deployment)
        )

    @with_json_fixture("deployments/get.json")
    def test_response_deployments_remove_namespace_from_all_app_ids(
        self, fixture
    ):
        deployment = MarathonDeployment.from_json(fixture[0])
        self.filter.response_deployment(self.user, deployment, deployment)

        self.assertEqual(deployment.affected_apps, ["/foo"])

        current_action_apps = [
            action.app for action in deployment.current_actions
        ]
        self.assertEqual(current_action_apps, ["/foo"])

        actions = [step.actions for step in deployment.steps]
        step_apps = [action.app for action in chain.from_iterable(actions)]
        self.assertEqual(step_apps, ["/foo", "/foo"])

    @with_json_fixture("../fixtures/tasks/get.json")
    def test_response_tasks_remove_namespace_from_all_tasks(
        self, tasks_get_fixture
    ):
        task = MarathonTask.from_json(tasks_get_fixture["tasks"][0])
        task.id = "dev_" + task.id
        task.app_id = "/dev" + task.app_id
        filtered_task = self.filter.response_task(self.user, task, task)
        self.assertEqual(
            "waiting.01339ffa-ce9c-11e7-8144-2a27410e5638", filtered_task.id
        )
        self.assertEqual("/waiting", filtered_task.app_id)

    @with_json_fixture("../fixtures/tasks/get.json")
    def test_response_tasks_returns_none_if_group_outside_current_namespace(
        self, tasks_get_fixture
    ):
        task = MarathonTask.from_json(tasks_get_fixture["tasks"][0])
        task.id = "othernamespace_" + task.id
        task.app_id = "/othernamespace" + task.app_id
        self.assertIsNone(self.filter.response_task(self.user, task, task))

    @with_json_fixture("../fixtures/queue/get.json")
    def test_response_queue_return_none_if_queue_outside_namespace(
        self, queue_get_fixture
    ):
        queue = MarathonQueueItem.from_json(queue_get_fixture["queue"][0])
        self.assertIsNone(self.filter.response_queue(self.user, queue, queue))

    @with_json_fixture("../fixtures/queue/get.json")
    def test_response_queue_remove_namespace_from_app_name(
        self, queue_get_fixture
    ):
        queue = MarathonQueueItem.from_json(queue_get_fixture["queue"][1])
        filtered_queue = self.filter.response_queue(self.user, queue, queue)
        self.assertEqual("/waiting", filtered_queue.app.id)

    @with_json_fixture("../fixtures/queue/get.json")
    def test_response_queue_return_none_if_namespace_has_same_prefix(
        self, queue_get_fixture
    ):
        """
        Mesmo o namespace da app tendo o mesmo prefixo, devemos reconhecer que a queue não
        pertence ao nosso namespace
        """
        queue = MarathonQueueItem.from_json(queue_get_fixture["queue"][1])
        queue.app.id = "/developers/app"
        self.assertIsNone(self.filter.response_queue(self.user, queue, queue))
