
from mock import patch
from unittest import TestCase
import hollowman.upstream

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

