

import unittest
import json
from flask import Response as FlaskResponse
from marathon.models.group import MarathonGroup

from http import HTTPStatus


from hollowman.app import application
from hollowman.models import Account, User
from hollowman.marathonapp import AsgardApp
from hollowman.filters.defaultscale import DefaultScaleFilter
from hollowman.http_wrappers.response import Response
from tests.utils import with_json_fixture

class TestNamespaceFilter(unittest.TestCase):

    @with_json_fixture("single_full_app.json")
    def setUp(self, single_full_app_fixture):
        self.filter = DefaultScaleFilter()
        self.request_app = AsgardApp.from_json(single_full_app_fixture)
        self.original_app = AsgardApp.from_json(single_full_app_fixture)
        self.account = Account(name="Dev Account", namespace="dev", owner="company")
        self.user = User(tx_email="user@host.com.br")
        self.user.current_account = self.account

    def test_create_app_with_zero_instances(self):
        self.request_app.instances = 0
        filtered_app = self.filter.write(self.user, self.request_app, AsgardApp())
        self.assertTrue("hollowman.default_scale" not in filtered_app.labels.keys(), "Não deveria ter adicionado label default_scale")

    def test_update_suspended_app_set_instances_to_zero(self):
        """
        Nesse caso não devemos mexer no default scale.
        """
        self.request_app.instances = 0
        self.original_app.instances = 0
        self.request_app.labels["hollowman.default_scale"] = "5"
        filtered_app = self.filter.write(self.user, self.request_app, self.original_app)
        self.assertEqual("5", filtered_app.labels["hollowman.default_scale"])

    def test_update_running_app_set_instances_to_zero(self):
        self.original_app.instances = 10
        self.request_app.instances = 0
        filtered_app = self.filter.write(self.user, self.request_app, self.original_app)
        self.assertEqual("10", filtered_app.labels["hollowman.default_scale"])

    def test_scale_down_should_not_change_default_scale(self):
        self.original_app.instances = 10
        self.request_app.instances = 7
        filtered_app = self.filter.write(self.user, self.request_app, self.original_app)
        self.assertTrue("hollowman.default_scale" not in filtered_app.labels.keys(), "Não deveria ter adicionado label default_scale")

