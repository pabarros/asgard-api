
import unittest

from hollowman.filters.appname import AddAppNameFilter

from tests import ContextStub, RequestStub
import mock

from marathon.models.app import MarathonApp

class TestAppNameFilterTest(unittest.TestCase):


    def setUp(self):
        self.ctx = ContextStub()
        self.filter = AddAppNameFilter()

    def test_add_appname_app_with_other_params(self):
        data_ = {
            "id": "/my/app/foo",
            "container": {
                "docker": {
                    "parameters": [
                        {
                            "key": "dns",
                            "value": "172.17.0.1"
                        }
                    ]
                }
            } 
        }
        with mock.patch.object(self, "ctx") as ctx_mock:
            ctx_mock.marathon_client.get_app.return_value = MarathonApp(**data_)
            request = RequestStub(path="/v2/apps//my/app/foo", data=data_, method="PUT")

            self.ctx.request = request
            modified_request = self.filter.run(self.ctx)
            result_data = modified_request.get_json()
            self.assertEqual(2, len(result_data['container']['docker']['parameters']))

            docker_params = result_data['container']['docker']['parameters']
            self.assertEqual("label", docker_params[1]['key'])
            self.assertEqual("hollowman.appname=/my/app/foo", docker_params[1]['value'])

    def test_add_appname_creating_new_app(self):
        data_ = {
            "id": "/my/app/newapp",
            "container": {
                "docker": {
                }
            } 
        }
        with mock.patch.object(self, "ctx") as ctx_mock:
            ctx_mock.marathon_client.get_app.return_value = MarathonApp()
            request = RequestStub(path="/v2/apps//my/app/foo", data=data_, method="PUT")
            self.ctx.request = request
            modified_request = self.filter.run(self.ctx)
            result_data = modified_request.get_json()

            docker_params = result_data['container']['docker']['parameters']
            self.assertEqual(1, len(docker_params))
            self.assertEqual("label", docker_params[0]['key'])
            self.assertEqual("hollowman.appname=/my/app/newapp", docker_params[0]['value'])

    def test_add_appname_app_without_params(self):
        data_ = {
            "id": "/my/app/no_params",
            "container": {
                "docker": {
                }
            } 
        }
        with mock.patch.object(self, "ctx") as ctx_mock:
            ctx_mock.marathon_client.get_app.return_value = MarathonApp(**data_)
            request = RequestStub(path="/v2/apps//my/app/foo", data=data_, method="PUT")
            self.ctx.request = request
            modified_request = self.filter.run(self.ctx)
            result_data = modified_request.get_json()

            docker_params = result_data['container']['docker']['parameters']
            self.assertEqual(1, len(docker_params))
            self.assertEqual("label", docker_params[0]['key'])
            self.assertEqual("hollowman.appname=/my/app/no_params", docker_params[0]['value'])

    def test_override_label_param_if_already_exist(self):
        """
        We always set the param, even if it hs a different value.
        """
        data_ = {
            "id": "/my/app/with_appname_param",
            "container": {
                "docker": {
                    "parameters": [
                        {
                            "key": "dns",
                            "value": "172.17.0.1"
                        },
                        {
                            "key": "label",
                            "value": "hollowman.appname=/my/other/app"
                        }
                    ]
                }
            } 
        }
        with mock.patch.object(self, "ctx") as ctx_mock:
            ctx_mock.marathon_client.get_app.return_value = MarathonApp(**data_)
            request = RequestStub(path="/v2/apps//my/app/foo", data=data_, method="PUT")
            self.ctx.request = request
            modified_request = self.filter.run(self.ctx)
            result_data = modified_request.get_json()

            docker_params = result_data['container']['docker']['parameters']
            self.assertEqual(2, len(docker_params))
            self.assertEqual("label", docker_params[1]['key'])
            self.assertEqual("hollowman.appname=/my/app/with_appname_param", docker_params[1]['value'])

