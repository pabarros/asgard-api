import asynctest
from asynctest.mock import CoroutineMock, call, Mock
from asgard.http.client import _HttpClientMaker, _HttpClient


class HttpClientTest(asynctest.TestCase):
    async def setUp(self):
        self.http_client = _HttpClientMaker()
        self._session_mock = CoroutineMock(get=CoroutineMock(), close=CoroutineMock())
        self.http_client._session = CoroutineMock()

    async def test_pass_args_to_shared_client_session(self):
        session_class_mock = Mock(return_value=self._session_mock)
        client = _HttpClient(
            session_class_mock,
            "https://httpbin.org/ip",
            "GET",
            44,
            timeout=10,
            data={"key": "OK"},
        )
        async with client:
            session_class_mock.assert_called_with(44, timeout=10, data={"key": "OK"})

    async def test_use_correct_http_method_when_entering_context_get(self):
        self.fail()

    async def test_use_correct_http_method_when_entering_context_post(self):
        self.fail()

    async def test_use_correct_http_method_when_entering_context_put(self):
        self.fail()

    async def test_use_correct_http_method_when_entering_context_delete(self):
        self.fail()

    async def test_close_shared_session_on_context_exit(self):
        self.fail()
