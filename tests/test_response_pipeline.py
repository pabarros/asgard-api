
from flask import Response as FlaskResponse
from copy import deepcopy
import unittest
import json
import responses

from hollowman.app import application
from hollowman.http_wrappers.response import Response
from hollowman.dispatcher import dispatch_response_pipeline
from hollowman import conf
from hollowman.models import User, Account

from tests.utils import with_json_fixture


class RemoveNSFilter:
    def response(self, user, response_app, original_app):
        response_app.id = response_app.id.replace("/dev/", "/")
        return response_app


class ResponsePipelineTest(unittest.TestCase):

    @with_json_fixture("single_full_app.json")
    def setUp(self, single_full_app_fixture):
        self.single_full_app_fixture = single_full_app_fixture
        self.user = User(tx_name="User", tx_email="user@host.com")
        self.user.current_account = Account(name="Some Account", namespace="dev", owner="company")
        responses.start()

    def tearDown(self):
        responses.stop()

    def test_response_has_app_modified_by_filter(self):
        """
        Certificamos que um request em uma app, roda o pipeline
        e essa app pode ser modificada por algum filtro
        """
        with application.test_request_context("/v2/apps/dev/foo", method="GET") as ctx:
            single_full_app_one = deepcopy(self.single_full_app_fixture)
            single_full_app_one['id'] = '/dev/foo'

            _url = conf.MARATHON_ENDPOINT + '/v2/apps//dev/foo'
            responses.add(method='GET',
                     url=_url,
                     body=json.dumps({'app': single_full_app_one}),
                     status=200)
            original_response = FlaskResponse(response=json.dumps({'app': single_full_app_one}),
                                              status=200,
                                              headers={})

            response_wrapper = Response(ctx.request, original_response)
            final_response = dispatch_response_pipeline(user=self.user,
                                                        response=response_wrapper,
                                                       filters_pipeline=(RemoveNSFilter(),))
            self.assertEqual(200, final_response.status_code)
            self.assertEqual("/foo", json.loads(final_response.data)['app']['id'])


    def test_response_has_list_of_apps_modified_by_filters(self):
        """
        Certificamos que uma lista de apps pode ser modificada por algum
        filtro de response.
        """
        with application.test_request_context("/v2/apps/", method="GET") as ctx:
            single_full_app_one = deepcopy(self.single_full_app_fixture)
            single_full_app_one['id'] = '/dev/foo'

            single_full_app_two = deepcopy(self.single_full_app_fixture)
            single_full_app_two['id'] = '/dev/other-app'

            responses.add(method='GET', url=conf.MARATHON_ENDPOINT + '/v2/apps//dev/foo',
                     body=json.dumps({'app': single_full_app_one}), status=200)
            responses.add(method='GET', url=conf.MARATHON_ENDPOINT + '/v2/apps//dev/other-app',
                     body=json.dumps({'app': single_full_app_two}), status=200)

            original_response = FlaskResponse(response=json.dumps({'apps': [single_full_app_one, single_full_app_two]}),
                                              status=200, headers={})

            response_wrapper = Response(ctx.request, original_response)
            final_response = dispatch_response_pipeline(user=self.user,
                                                        response=response_wrapper,
                                                       filters_pipeline=(RemoveNSFilter(),))
            self.assertEqual(200, final_response.status_code)
            self.assertEqual("/foo", json.loads(final_response.data)['apps'][0]['id'])
            self.assertEqual("/other-app", json.loads(final_response.data)['apps'][1]['id'])

