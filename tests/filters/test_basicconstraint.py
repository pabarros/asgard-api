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
        self.assertEqual(result_app.constraints, list(self.filter.constraints))

    def test_it_doesnt_change_current_constraints_if_constraints_isnt_empty(self):
        original_constraints = deepcopy(self.request_app.constraints)
        result_app = self.filter.write(self.user, self.request_app, self.original_app)
        self.assertEqual(original_constraints, result_app.constraints)

    def test_request_app_has_all_constraints_original_app_constraints_is_empty(self):
        self.request_app.constraints = list(self.filter.constraints)
        self.original_app.constraints = []
        result_app = self.filter.write(self.user, self.request_app, self.original_app)

        self.assertEqual(result_app.constraints, list(self.filter.constraints))

    def test_request_app_has_single_constraint_original_app_constraints_is_empty(self):
        self.request_app.constraints = [self.filter.constraints[0]]
        self.original_app.constraints = []
        result_app = self.filter.write(self.user, self.request_app,
                                       self.original_app)

        self.assertEqual(result_app.constraints, [self.filter.constraints[0]])
