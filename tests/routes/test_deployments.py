import json
from typing import Dict
from unittest import TestCase
from unittest.mock import patch

from responses import RequestsMock

from hollowman import conf
from hollowman.app import application
from hollowman.auth.jwt import jwt_auth, jwt_generate_user_info

from tests.base import BaseApiTests
from tests.utils import with_json_fixture


class DeploymentsTests(BaseApiTests, TestCase):
    def make_auth_header(self, user, account) -> Dict[str, str]:
        jwt_token = jwt_auth.jwt_encode_callback(
            jwt_generate_user_info(user, account)
        )
        return {"Authorization": "JWT {}".format(jwt_token.decode("utf-8"))}

    @with_json_fixture("deployments/get.json")
    def test_v2_deployments_get(self, fixture):
        with application.test_client() as client, RequestsMock() as rsps:
            rsps.add(
                url=f"{conf.MARATHON_ADDRESSES[0]}/v2/deployments",
                body=json.dumps(fixture),
                method="GET",
                status=200,
            )
            response = client.get("/v2/deployments", headers=self.auth_header)
            self.assertEqual(
                json.loads(response.data),
                [
                    {
                        "affectedApps": ["/foo"],
                        "currentActions": [
                            {
                                "action": "ScaleApplication",
                                "app": "/foo",
                                "apps": None,
                                "pod": None,
                                "type": None,
                                "readinessCheckResults": [
                                    {
                                        "taskId": "foo.c9de6033",
                                        "lastResponse": {
                                            "body": "{}",
                                            "contentType": "application/json",
                                            "status": 500,
                                        },
                                        "name": "myReadyCheck",
                                        "ready": False,
                                    }
                                ],
                            }
                        ],
                        "currentStep": 2,
                        "id": "97c136bf-5a28-4821-9d94-480d9fbb01c8",
                        "steps": [
                            {
                                "actions": [
                                    {
                                        "action": "StartApplication",
                                        "app": "/foo",
                                        "apps": None,
                                        "pod": None,
                                        "type": None,
                                        "readinessCheckResults": None,
                                    }
                                ]
                            },
                            {
                                "actions": [
                                    {
                                        "action": "ScaleApplication",
                                        "app": "/foo",
                                        "apps": None,
                                        "pod": None,
                                        "type": None,
                                        "readinessCheckResults": None,
                                    }
                                ]
                            },
                        ],
                        "totalSteps": 2,
                        "version": "2015-09-30T09:09:17.614Z",
                    }
                ],
            )

    @with_json_fixture("deployments/delete.json")
    def test_v2_deployments_delete(self, fixture):
        with application.test_client() as client, RequestsMock() as rsps, patch(
            "hollowman.request_handlers.Deployments._apply_response_filters"
        ) as _apply_response_filters:
            response_data = json.dumps(fixture)
            rsps.add(
                url=f"{conf.MARATHON_ADDRESSES[0]}/v2/deployments/foo",
                body=response_data,
                method="DELETE",
                status=200,
            )
            response = client.delete(
                "/v2/deployments/foo", headers=self.auth_header
            )

            self.assertFalse(_apply_response_filters.called)
            self.assertEqual(json.loads(response.data), fixture)

    @with_json_fixture("../fixtures/deployments/get-multi-namespace.json")
    def test_deployments_remove_all_from_other_namespaces(
        self, multi_namespace_deployments_fixture
    ):
        with application.test_client() as client, RequestsMock() as rsps:
            rsps.add(
                url=f"{conf.MARATHON_ADDRESSES[0]}/v2/deployments",
                body=json.dumps(multi_namespace_deployments_fixture),
                method="GET",
                status=200,
            )
            response = client.get("/v2/deployments", headers=self.auth_header)
            response_data = json.loads(response.data)
            self.assertEqual(1, len(response_data))
            self.assertEqual("/foo", response_data[0]["affectedApps"][0])
