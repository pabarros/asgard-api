import unittest

from marathon.models.constraint import MarathonConstraint

from hollowman.filters.owner import AddOwnerConstraintFilter
from hollowman.marathonapp import AsgardApp
from hollowman.models import Account, HollowmanSession, User
from tests import rebuild_schema
from tests.utils import with_json_fixture


class OwnerFilterTest(unittest.TestCase):
    @with_json_fixture("single_full_app.json")
    def setUp(self, single_full_app_fixture):
        self.filter = AddOwnerConstraintFilter()
        rebuild_schema()
        self.session = HollowmanSession()
        self.user = User(
            tx_email="user@host.com.br",
            tx_name="John Doe",
            tx_authkey="69ed620926be4067a36402c3f7e9ddf0",
        )
        self.account_dev = Account(
            id=4, name="Dev Team", namespace="dev", owner="company"
        )
        self.user.accounts = [self.account_dev]
        self.session.add(self.user)
        self.session.add(self.account_dev)
        self.session.commit()

        self.request_app = AsgardApp.from_json(single_full_app_fixture)
        self.original_app = AsgardApp.from_json(single_full_app_fixture)
        self.user.current_account = self.account_dev

    def test_create_app_add_constraint_app_with_no_constraint(self):
        self.request_app.constraints = []
        filtered_app = self.filter.write(
            self.user, self.request_app, AsgardApp()
        )

        owner_constraint = filtered_app.get_constraints_by_name("owner")
        self.assertEqual(1, len(filtered_app.constraints))
        self.assertEqual(1, len(owner_constraint))
        self.assertEqual(self.account_dev.owner, owner_constraint[0].value)

    def test_update_app_add_constraint_app_with_no_constraint(self):
        self.request_app.constraints = []
        self.original_app.constraints = []
        filtered_app = self.filter.write(
            self.user, self.request_app, self.original_app
        )

        owner_constraint = filtered_app.get_constraints_by_name("owner")
        self.assertEqual(1, len(filtered_app.constraints))
        self.assertEqual(1, len(owner_constraint))
        self.assertEqual(self.account_dev.owner, owner_constraint[0].value)

    def test_create_app_constraint_exist_with_wrong_value(self):
        self.request_app.constraints.append(
            MarathonConstraint(
                field="owner", operator="LIKE", value="other-owner"
            )
        )
        filtered_app = self.filter.write(
            self.user, self.request_app, AsgardApp()
        )

        owner_constraint = filtered_app.get_constraints_by_name("owner")
        self.assertEqual(2, len(filtered_app.constraints))
        self.assertEqual(1, len(owner_constraint))
        self.assertEqual(self.account_dev.owner, owner_constraint[0].value)

    def test_update_app_constraint_exist_with_wrong_value(self):
        self.request_app.constraints.append(
            MarathonConstraint(
                field="owner", operator="LIKE", value="other-owner"
            )
        )
        filtered_app = self.filter.write(
            self.user, self.request_app, self.original_app
        )

        owner_constraint = filtered_app.get_constraints_by_name("owner")
        self.assertEqual(2, len(filtered_app.constraints))
        self.assertEqual(1, len(owner_constraint))
        self.assertEqual(self.account_dev.owner, owner_constraint[0].value)

    def test_create_app_add_constraint_app_with_other_constraints(self):
        filtered_app = self.filter.write(
            self.user, self.request_app, AsgardApp()
        )

        owner_constraint = filtered_app.get_constraints_by_name("owner")
        self.assertEqual(2, len(filtered_app.constraints))
        self.assertEqual(1, len(owner_constraint))
        self.assertEqual(self.account_dev.owner, owner_constraint[0].value)

    def test_update_app_add_constraint_app_with_other_constraints(self):
        filtered_app = self.filter.write(
            self.user, self.request_app, self.original_app
        )

        owner_constraint = filtered_app.get_constraints_by_name("owner")
        self.assertEqual(2, len(filtered_app.constraints))
        self.assertEqual(1, len(owner_constraint))
        self.assertEqual(self.account_dev.owner, owner_constraint[0].value)

    def test_update_app_trying_to_remove_constraint(self):
        self.original_app.constraints.append(
            MarathonConstraint(
                field="owner", operator="LIKE", value=self.account_dev.owner
            )
        )
        filtered_app = self.filter.write(
            self.user, self.request_app, self.original_app
        )

        owner_constraint = filtered_app.get_constraints_by_name("owner")
        self.assertEqual(2, len(filtered_app.constraints))
        self.assertEqual(
            "srv2.*", filtered_app.get_constraints_by_name("hostname")[0].value
        )
        self.assertEqual(1, len(owner_constraint))
        self.assertEqual(self.account_dev.owner, owner_constraint[0].value)
