import unittest
from copy import deepcopy
from unittest.mock import Mock

from hollowman.filters.basicconstraint import BasicConstraintFilter
from hollowman.marathonapp import SieveMarathonApp
from tests.utils import get_fixture


class TestBasicConstraintFilter(unittest.TestCase):
    def setUp(self):
        self.single_full_app_fixture = get_fixture("single_full_app.json")
        self.filter = BasicConstraintFilter()
        self.request_app = SieveMarathonApp.from_json(self.single_full_app_fixture)
        self.original_app = Mock()
        self.user = Mock()

    def test_it_adds_default_constraints_if_none_present(self):
        self.request_app.constraints = []
        result_app = self.filter.write(self.user, self.request_app, self.original_app)
        self.assertEqual(self.request_app.constraints, list(self.filter.required_constraints))

    def test_it_doesnt_change_current_constraints_if_constraints_isnt_empty(self):
        original_constraints = deepcopy(self.request_app.constraints)
        result_app = self.filter.write(self.user, self.request_app, self.original_app)
        self.assertEqual(original_constraints, self.request_app.constraints)
