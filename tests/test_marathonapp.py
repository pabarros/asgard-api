
import unittest

from marathon.models.constraint import MarathonConstraint

from hollowman.marathonapp import AsgardMarathonApp

from tests.utils import with_json_fixture

class SieveMarathonAppTest(unittest.TestCase):

    @with_json_fixture("single_full_app.json")
    def setUp(self, single_full_app_fixture):
        self.sieve_marathon_app = AsgardMarathonApp.from_json(single_full_app_fixture)

    def test_remove_single_value_constraint(self):
        self.sieve_marathon_app.remove_constraints_by_name("hostname")
        self.assertEqual(0, len(self.sieve_marathon_app.constraints))

    def test_remove_multi_value_constraint(self):
        self.sieve_marathon_app.constraints.append(MarathonConstraint(field="work", operator="LIKE", value="w1"))
        self.sieve_marathon_app.constraints.append(MarathonConstraint(field="work", operator="LIKE", value="w2"))
        self.assertEqual(3, len(self.sieve_marathon_app.constraints))
        self.sieve_marathon_app.remove_constraints_by_name("work")

        self.assertEqual(1, len(self.sieve_marathon_app.constraints))
        self.assertEqual("hostname", self.sieve_marathon_app.constraints[0].field)

    def test_remove_inexistent_constraint(self):
        self.sieve_marathon_app.remove_constraints_by_name("work")

        self.assertEqual(1, len(self.sieve_marathon_app.constraints))
        self.assertEqual("hostname", self.sieve_marathon_app.constraints[0].field)

    def test_get_by_name_single_value(self):
        hostname_constraint = self.sieve_marathon_app.get_constraints_by_name("hostname")
        self.assertEqual(1, len(hostname_constraint))
        self.assertEqual("srv2.*", hostname_constraint[0].value)

    def test_get_by_name_multi_value(self):
        self.sieve_marathon_app.constraints.append(MarathonConstraint(field="work", operator="LIKE", value="w1"))
        self.sieve_marathon_app.constraints.append(MarathonConstraint(field="work", operator="LIKE", value="w2"))

        self.assertEqual(3, len(self.sieve_marathon_app.constraints))

        work_constraint = self.sieve_marathon_app.get_constraints_by_name("work")
        self.assertEqual(2, len(work_constraint))
        self.assertEqual(set(["w1", "w2"]), set([c.value for c in work_constraint]))

    def test_get_by_name_inexistent(self):
        work_constraint = self.sieve_marathon_app.get_constraints_by_name("work")
        self.assertEqual(0, len(work_constraint))

    def test_has_constraint_it_exists(self):
        self.assertTrue(self.sieve_marathon_app.has_constraint("hostname"))

    def test_has_constraint_it_does_not_exist(self):
        self.assertFalse(self.sieve_marathon_app.has_constraint("owner"))

    def test_label_update_non_existent_label(self):
        app = AsgardMarathonApp(labels={"label1": "value1"})
        app.update_label("label2", "value2")

        self.assertEqual(2, len(app.labels.keys()))
        self.assertEqual("value2", app.labels["label2"])

    def test_label_update_existing_label(self):
        app = AsgardMarathonApp(labels={"label1": "value1"})
        app.update_label("label1", "new-value")

        self.assertEqual(1, len(app.labels.keys()))
        self.assertEqual("new-value", app.labels["label1"])

