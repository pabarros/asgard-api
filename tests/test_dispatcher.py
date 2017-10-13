from unittest import TestCase
from unittest.mock import Mock

from marathon.models.app import MarathonApp

from hollowman.dispatcher import dispatch, merge_marathon_apps, FILTERS_PIPELINE
from hollowman.hollowman_flask import OperationType
from tests.utils import with_json_fixture


class DispatcherTests(TestCase):

    @with_json_fixture("single_full_app.json")
    def test_it_calls_registered_filters_in_order(self, single_full_app_fixture):
        request_app = MarathonApp.from_json(single_full_app_fixture)
        original_app = MarathonApp()
        merged_app = merge_marathon_apps(original_app, request_app)
        filters = [Mock(), Mock()]
        for f in filters:
            f.read.return_value = request_app
        user = Mock()

        dispatch(
            [OperationType.READ], user, request_app, original_app,
            filters_pipeline={OperationType.READ: filters}
        )

        filters[0].read.assert_called_once_with(user, merged_app, original_app)
        filters[1].read.assert_called_once_with(user, merge_marathon_apps(original_app, filters[0].read.return_value), original_app)

    @with_json_fixture("single_full_app.json")
    def test_it_calls_registered_filters_with_request_app_merged(self, single_full_app_fixture):
        filters = [Mock()]
        original_app = MarathonApp.from_json(single_full_app_fixture)
        request_app = MarathonApp.from_json({"env": {"FOO": "BAR"}})
        merged_app = merge_marathon_apps(original_app, request_app)
        user = Mock()

        dispatch(
            [OperationType.WRITE], user, request_app, original_app,
            filters_pipeline={OperationType.WRITE: filters}
        )

        filters[0].write.assert_called_once_with(user, merged_app, original_app)

    def test_it_doesnt_calls_filters_for_other_operations(self):
        filters = [Mock(), Mock()]
        request_app = Mock()
        user = Mock()
        app = Mock()

        dispatch(
            [OperationType.READ], user, request_app, app,
            filters_pipeline={OperationType.READ: [], OperationType.WRITE: filters}
        )

        for filter in filters:
            filter.assert_not_called()

    @with_json_fixture("single_full_app.json")
    def test_merge_two_marathon_apps_modified_app_no_container_info(self, single_full_app_fixture):
        """
        Certifica que uma app que não tem as informações de container, não apaga isso da app resultante.
        """
        original_app = MarathonApp.from_json(single_full_app_fixture)
        self.assertTrue(original_app.container)
        modified_app = MarathonApp.from_json({"mem": 32})

        merged_app = merge_marathon_apps(original_app, modified_app)
        self.assertEqual(32, merged_app.mem)
        self.assertTrue(merged_app.container)
        self.assertTrue(merged_app.constraints)

    @with_json_fixture("single_full_app.json")
    def test_merge_two_marathon_apps_modified_one_docker_info(self, single_full_app_fixture):
        original_app = MarathonApp.from_json(single_full_app_fixture)
        modified_app = MarathonApp.from_json(single_full_app_fixture)

        modified_app.container.docker.force_pull_image = True
        modified_app.container.docker.privileged = True

        merged_app = merge_marathon_apps(original_app, modified_app)
        self.assertTrue(merged_app.container.docker.force_pull_image)
        self.assertTrue(merged_app.container.docker.privileged)
        self.assertEqual("mesosphere:marathon/latest", merged_app.container.docker.image)

    @with_json_fixture("single_full_app.json")
    def test_merge_two_marathon_apps_modified_only_env_vars(self, single_full_app_fixture):
        original_app = MarathonApp.from_json(single_full_app_fixture)
        new_envs = {"foo": "bar"}
        modified_app = MarathonApp.from_json({"env": new_envs})

        merged_app = merge_marathon_apps(original_app, modified_app)
        self.assertFalse(merged_app.container.docker.privileged)
        self.assertEqual("mesosphere:marathon/latest", merged_app.container.docker.image)
        self.assertDictEqual(new_envs, merged_app.env)
        self.assertTrue(merged_app.constraints)
        self.assertTrue(merged_app.labels)

    @with_json_fixture("single_full_app.json")
    def test_merge_two_marathon_apps_when_creating_app(self, single_full_app_fixture):
        modified_app = MarathonApp.from_json(single_full_app_fixture)
        original_app = MarathonApp()

        merged_app = merge_marathon_apps(original_app, modified_app)
        self.assertFalse(merged_app.container.docker.privileged)
        self.assertEqual("mesosphere:marathon/latest", merged_app.container.docker.image)
        self.assertTrue(merged_app.constraints)
        self.assertTrue(merged_app.labels)

    @with_json_fixture("single_full_app.json")
    def test_assert_all_filters_run_with_unauthenticated_request(self, single_full_app_fixture):
        marathon_app = MarathonApp.from_json(single_full_app_fixture)
        for filter_ in FILTERS_PIPELINE[OperationType.WRITE]:
            filtered_app = filter_.write(None, marathon_app, marathon_app)
            self.assertTrue(marathon_app is filtered_app)
