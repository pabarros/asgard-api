
from flask import Response as FlaskResponse
from copy import deepcopy
import unittest
import json
import responses

from marathon.models import MarathonConstraint, MarathonHealthCheck
from marathon.models.app import MarathonUpgradeStrategy

from hollowman.app import application
from hollowman.http_wrappers.response import Response
from hollowman.http_wrappers.base import HTTPWrapper
from hollowman.dispatcher import dispatch, REMOVABLE_KEYS
from hollowman import conf
from hollowman.hollowman_flask import OperationType, FilterType
from hollowman.models import User, Account
from hollowman.marathonapp import SieveMarathonApp

from tests.utils import with_json_fixture


class RequestPipelineTest(unittest.TestCase):

    @with_json_fixture("single_full_app.json")
    def setUp(self, single_full_app_fixture):
        self.single_full_app_fixture = single_full_app_fixture
        self.user = User(tx_name="User", tx_email="user@host.com")
        self.user.current_account = Account(name="Some Account", namespace="dev", owner="company")

    def test_update_app_remove_all_constraints(self):
        """
        Certifica que um request que remove todas as constraints,
        remove essas constraints na app original
        """
        class DummyFilter:
            def write(self, user, request_app, original_app):
                return request_app

        pipeline = {
                OperationType.WRITE: [DummyFilter(), ]
        }

        request_data = {"constraints": []}
        request_app = SieveMarathonApp.from_json(request_data)
        original_app = SieveMarathonApp.from_json(deepcopy(self.single_full_app_fixture))

        with application.test_request_context("/v2/apps/foo",
                                              method="PUT",
                                              data=json.dumps(request_data),
                                              headers={"Content-type": "application/json"}) as ctx:
            filtered_app = dispatch([OperationType.WRITE], self.user, request_app, original_app, filters_pipeline=pipeline)
            self.assertEqual(0, len(filtered_app.constraints))
            self._check_other_fields("constraints", filtered_app)

    def test_update_app_change_all_constraints(self):
        """
        Devemos respeitar as constraints quem estão da request,
        elas devem substituir as constrains da app original
        """
        class DummyFilter:
            def write(self, user, request_app, original_app):
                return request_app

        pipeline = {
                OperationType.WRITE: [DummyFilter(), ]
        }

        request_data = {"constraints": [["hostname", "LIKE", "myhost"]]}
        request_app = SieveMarathonApp.from_json(request_data)
        original_app = SieveMarathonApp.from_json(deepcopy(self.single_full_app_fixture))

        with application.test_request_context("/v2/apps/foo",
                                              method="PUT",
                                              data=json.dumps(request_data),
                                              headers={"Content-type": "application/json"}) as ctx:
            filtered_app = dispatch([OperationType.WRITE], self.user, request_app, original_app, filters_pipeline=pipeline)
            self.assertEqual(1, len(filtered_app.constraints))
            self.assertEqual(["hostname", "LIKE", "myhost"], filtered_app.constraints[0].json_repr())
            self._check_other_fields("constraints", filtered_app)

    def test_preserve_constraints_added_by_filter(self):
        """
        Certifica que quando um request remove todas as constraints e algum filtro adiciona novas
        constraints, essas constraints adicionadas pelo filtro são preservadas
        """
        class AddNewConstraintFilter:
            def write(self, user, request_app, original_app):
                request_app.constraints.append(MarathonConstraint.from_json("key:LIKE:value".split(":")))
                return request_app

        pipeline = {
                OperationType.WRITE: [AddNewConstraintFilter(), ]
        }

        request_data = {"constraints": []}
        request_app = SieveMarathonApp.from_json(request_data)
        original_app = SieveMarathonApp.from_json(deepcopy(self.single_full_app_fixture))

        with application.test_request_context("/v2/apps/foo",
                                              method="PUT",
                                              headers={"Content-type": "application/json"},
                                              data=json.dumps(request_data)) as ctx:

            filtered_app = dispatch([OperationType.WRITE], self.user, request_app, original_app, filters_pipeline=pipeline)
            self.assertEqual(1, len(filtered_app.constraints))
            self._check_other_fields("constraints", filtered_app)

    def _check_other_fields(self, skip_field_names, filtered_app):
        json_repr = json.loads(json.dumps(filtered_app, cls=HTTPWrapper.json_encoder))

        for key in REMOVABLE_KEYS:
            if key not in skip_field_names:
                self.assertEqual(self.single_full_app_fixture[key], json_repr[key], "key `{}` foi alterada".format(key))

    def test_preserve_labels_added_by_filter(self):
        class AddNewLabelFilter:
            def write(self, user, request_app, original_app):
                request_app.labels["label1"] = "value1"
                return request_app

        pipeline = {
                OperationType.WRITE: [AddNewLabelFilter(), ]
        }
        request_data = {"labels": {}}

        request_app = SieveMarathonApp.from_json(request_data)
        original_app = SieveMarathonApp.from_json(deepcopy(self.single_full_app_fixture))

        with application.test_request_context("/v2/apps/foo",
                                              method="PUT",
                                              headers={"Content-type": "application/json"},
                                              data=json.dumps(request_data)) as ctx:

            filtered_app = dispatch([OperationType.WRITE], self.user, request_app, original_app, filters_pipeline=pipeline)
            self.assertEqual(1, len(filtered_app.labels.keys()))
            self.assertEqual({"label1": "value1"}, filtered_app.labels)
            self._check_other_fields("labels", filtered_app)

    def test_preserve_upgrade_strategy_added_by_filter(self):
        class AddNewUpgradeStrategyFilter:
            def write(self, user, request_app, original_app):
                us_data = {
                    "maximumOverCapacity": 1,
                    "minimumHealthCapacity": 0.75
                }
                request_app.upgrade_strategy = MarathonUpgradeStrategy.from_json(us_data)
                return request_app

        pipeline = {
                OperationType.WRITE: [AddNewUpgradeStrategyFilter(), ]
        }
        # Simulando uma app que veio sem o campo "upgradeStrategy"
        request_data = {}

        request_app = SieveMarathonApp.from_json(request_data)
        original_app = SieveMarathonApp.from_json(deepcopy(self.single_full_app_fixture))

        with application.test_request_context("/v2/apps/foo",
                                              method="PUT",
                                              headers={"Content-type": "application/json"},
                                              data=json.dumps(request_data)) as ctx:

            filtered_app = dispatch([OperationType.WRITE], self.user, request_app, original_app, filters_pipeline=pipeline)

            self.assertEqual(1, filtered_app.upgrade_strategy.maximum_over_capacity)
            self.assertEqual(0.75, filtered_app.upgrade_strategy.minimum_health_capacity)
            self._check_other_fields("upgradeStrategy", filtered_app)

    def test_preserve_envs_added_by_filter(self):
        class AddNewEnvFilter:
            def write(self, user, request_app, original_app):
                request_app.env["env1"] = "env-value1"
                return request_app

        pipeline = {
                OperationType.WRITE: [AddNewEnvFilter(), ]
        }
        request_data = {"env": []}

        request_app = SieveMarathonApp.from_json(request_data)
        original_app = SieveMarathonApp.from_json(deepcopy(self.single_full_app_fixture))

        with application.test_request_context("/v2/apps/foo",
                                              method="PUT",
                                              headers={"Content-type": "application/json"},
                                              data=json.dumps(request_data)) as ctx:

            filtered_app = dispatch([OperationType.WRITE], self.user, request_app, original_app, filters_pipeline=pipeline)
            self.assertEqual(1, len(filtered_app.env.keys()))
            self.assertEqual({"env1": "env-value1"}, filtered_app.env)
            self._check_other_fields("env", filtered_app)

    def test_preserve_healthchecks_added_by_filter(self):
        class AddNewHealthCheckFilter:
            def write(self, user, request_app, original_app):
                hc_data = {
                    "command": None,
                    "gracePeriodSeconds": 30,
                    "intervalSeconds": 10,
                    "maxConsecutiveFailures": 3,
                    "path": "/marathon/healthcheck",
                    "portIndex": 0,
                    "protocol": "HTTP",
                    "timeoutSeconds": 5,
                    "ignoreHttp1xx": False
                }
                request_app.health_checks.append(MarathonHealthCheck.from_json(hc_data))
                return request_app

        pipeline = {
                OperationType.WRITE: [AddNewHealthCheckFilter(), ]
        }
        request_data = {
            "healthChecks": [
            ]
        }

        request_app = SieveMarathonApp.from_json(request_data)
        original_app = SieveMarathonApp.from_json(deepcopy(self.single_full_app_fixture))

        with application.test_request_context("/v2/apps/foo",
                                              method="PUT",
                                              headers={"Content-type": "application/json"},
                                              data=json.dumps(request_data)) as ctx:

            filtered_app = dispatch([OperationType.WRITE], self.user, request_app, original_app, filters_pipeline=pipeline)
            self.assertEqual(1, len(filtered_app.health_checks))
            self.assertEqual("/marathon/healthcheck", filtered_app.health_checks[0].json_repr()['path'])
            self._check_other_fields("healthChecks", filtered_app)


