

import unittest
import json
from flask import Response as FlaskResponse
from marathon.models.group import MarathonGroup

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

    def test_create_app_with_zero_instances(self):
        self.fail()

    def test_update_suspended_app_set_instances_to_zero(self):
        self.fail()

    def test_update_running_app_set_instances_to_zero(self):
        self.fail()
