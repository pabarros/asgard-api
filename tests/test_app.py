
from mock import patch
from unittest import TestCase
import hollowman.upstream
from hollowman.app import application
from collections import namedtuple


class DummyResponse(object):

    def __init__(self, headers={}):
        self.headers = headers
        self.content = None
        self.status_code = 200


class TestApp(TestCase):

    def test_remove_transfer_encoding_header(self):
        with patch('hollowman.upstream.replay_request', return_value=DummyResponse(headers={"Transfer-Encoding": "chunked"})):
            from hollowman.app import application
            with application.test_client() as client:
                response = client.get("/v2/apps")
                self.assertTrue("Content-Encoding" not in response.headers)
                response = client.get("/ui/main.css")
                self.assertTrue("Content-Encoding" not in response.headers)

    def test_index_path(self):
        response = application.test_client().open('/')

        self.assertEqual(response.status_code, 301)
        self.assertTrue('Location' in response.headers)

    def test_ui_path(self):
        Response = namedtuple(
            'Response',
            [
                "headers",
                "content",
                "status_code"
            ]
        )

        with patch('hollowman.app.replay_request') as replay_request_mock:
            replay_request_mock.return_value = Response(
                headers={
                    "foo": "bar",
                    "Transfer-Encoding": 123
                },
                content="foofoofoofoofoofoo",
                status_code=301
            )
            response = application.test_client().open('/ui/foo/bar')
            self.assertEqual(response.status_code, 301)

    # How can we test this ?
    # def test_apiv2_path(self):
    #     pass

    def test_fail_healthcheck(self):
        response = application.test_client().open('/healthcheck')
        self.assertTrue(response.status_code >= 400)

    def test_200_healthcheck(self):
        Response = namedtuple('Response', ["status_code"])

        with patch('hollowman.app.requests.get') as get_mock:
            get_mock.return_value = Response(status_code=200)
            response = application.test_client().open('/healthcheck')
            self.assertEqual(response.status_code, 200)
