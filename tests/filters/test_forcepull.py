#encoding: utf-8

from hollowman.filters.forcepull import ForcePullFilter
from unittest import TestCase

from marathon.models.app import MarathonApp
import mock
from tests.utils import with_json_fixture


class ForcePullTest(TestCase):

    def setUp(self):
        self.filter = ForcePullFilter()

    @with_json_fixture("single_full_app.json")
    def test_app_exists_forcepull_not_checked(self, single_full_app_fixture):
        original_app = MarathonApp.from_json(single_full_app_fixture)
        request_app = MarathonApp.from_json(single_full_app_fixture)
        request_app.container.docker.force_pull_image = False

        modified_request_app = self.filter.write(user=None, request_app=request_app, app=original_app)
        self.assertTrue(modified_request_app.container.docker.force_pull_image, True)

    @with_json_fixture("single_full_app.json")
    def test_creating_app_forcepull_not_checked(self, single_full_app_fixture):
        original_app = MarathonApp()
        request_app = MarathonApp.from_json(single_full_app_fixture)
        request_app.container.docker.force_pull_image = True

        modified_request_app = self.filter.write(user=None, request_app=request_app, app=original_app)
        self.assertTrue(modified_request_app.container.docker.force_pull_image, True)

    @with_json_fixture("single_full_app.json")
    def test_empty_request_app(self, single_full_app_fixture):
        """
        Isso acontece quando é um request de restart, por exemplo, onde o body do request é vazio.
        """
        original_app = MarathonApp.from_json(single_full_app_fixture)
        request_app = MarathonApp()

        modified_request_app = self.filter.write(user=None, request_app=request_app, app=original_app)
        self.assertTrue(request_app is modified_request_app)
