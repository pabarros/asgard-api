import unittest

import mock
from marathon.models.app import MarathonApp

from hollowman.filters.appname import AddAppNameFilter
from tests.utils import with_json_fixture


class TestAppNameFilter(unittest.TestCase):
    @with_json_fixture("single_full_app.json")
    def setUp(self, single_full_app_fixture):
        self.single_full_app_fixture = single_full_app_fixture
        self.original_app = MarathonApp.from_json(self.single_full_app_fixture)
        self.request_app = MarathonApp.from_json(single_full_app_fixture)
        self.filter = AddAppNameFilter()
        self.user = mock.MagicMock()

    def test_app_without_docker_info(self):
        """
        Não faz nada se a app não possui .container.docker.*
        """
        del self.request_app.container.docker
        modified_app = self.filter.write(
            self.user, self.request_app, self.original_app
        )
        self.assertTrue(modified_app is self.request_app)
        self.assertFalse(hasattr(modified_app.container, "docker"))

    def test_write_app_without_parameters(self):
        self.request_app.container.docker.parameters = []
        modified_app = self.filter.write(
            self.user, self.request_app, self.original_app
        )
        self.assertTrue(modified_app is self.request_app)
        self.assertEqual(1, len(modified_app.container.docker.parameters))
        self.assertEqual(
            "hollowman.appname=/foo",
            modified_app.container.docker.parameters[0]["value"],
        )

    def test_write_app_without_appame(self):
        modified_app = self.filter.write(
            self.user, self.request_app, self.original_app
        )
        self.assertTrue(modified_app is self.request_app)
        self.assertEqual(2, len(modified_app.container.docker.parameters))
        self.assertEqual(
            "hollowman.appname=/foo",
            modified_app.container.docker.parameters[1]["value"],
        )

    def test_write_app_with_wrong_appname(self):
        wrong_app_name_param = {
            "key": "label",
            "value": "hollowman.appname=/my/other/app/name",
        }
        self.request_app.container.docker.parameters.append(
            wrong_app_name_param
        )
        modified_app = self.filter.write(
            self.user, self.request_app, self.original_app
        )
        self.assertTrue(modified_app is self.request_app)
        self.assertEqual(2, len(modified_app.container.docker.parameters))
        self.assertEqual(
            "hollowman.appname=/foo",
            modified_app.container.docker.parameters[1]["value"],
        )

    def test_write_app_with_right_appname(self):
        wrong_app_name_param = {
            "key": "label",
            "value": "hollowman.appname=/foo",
        }
        self.request_app.container.docker.parameters.append(
            wrong_app_name_param
        )
        modified_app = self.filter.write(
            self.user, self.request_app, self.original_app
        )
        self.assertTrue(modified_app is self.request_app)
        self.assertEqual(2, len(modified_app.container.docker.parameters))
        self.assertEqual(
            "hollowman.appname=/foo",
            modified_app.container.docker.parameters[1]["value"],
        )

    def test_empty_body(self):
        wrong_app_name_param = {
            "key": "label",
            "value": "hollowman.appname=/foo",
        }
        modified_app = self.filter.write(
            self.user, self.request_app, self.original_app
        )
        self.assertTrue(modified_app is self.request_app)
