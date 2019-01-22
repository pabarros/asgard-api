from importlib import reload
import asynctest
from asynctest.mock import CoroutineMock, call, Mock
from asynctest import mock
from asgard.http.client import (
    _HttpClientMaker,
    _HttpClient,
    default_http_client_timeout,
)


class HttpClientTest(asynctest.TestCase):
    async def setUp(self):
        self._session_mock = CoroutineMock(
            post=CoroutineMock(),
            put=CoroutineMock(),
            delete=CoroutineMock(),
            get=CoroutineMock(),
            close=CoroutineMock(),
        )
        self.session_class_mock = Mock(return_value=self._session_mock)

    async def test_pass_args_to_shared_client_session(self):
        client = _HttpClient(
            self.session_class_mock,
            "https://httpbin.org/ip",
            "GET",
            44,
            timeout=10,
            data={"key": "OK"},
        )
        async with client:
            self.session_class_mock.assert_called_with(
                44, timeout=10, data={"key": "OK"}
            )

    async def test_shared_session_receives_default_timeout_config(self):
        client = _HttpClient(
            self.session_class_mock,
            "https://httpbin.org/ip",
            "GET",
            44,
            data={"key": "OK"},
        )
        async with client:
            self.session_class_mock.assert_called_with(
                44, timeout=default_http_client_timeout, data={"key": "OK"}
            )

    async def test_calls_apropriate_method_on_shared_session(self):
        client = _HttpClient(self.session_class_mock, "https://httpbin.org/ip", "POST")
        async with client:
            self.session_class_mock.assert_called_with(timeout=mock.ANY)
            client._session.post.assert_awaited_with("https://httpbin.org/ip")

    async def test_close_shared_session_on_context_exit(self):
        client = _HttpClient(self.session_class_mock, "https://httpbin.org/ip", "POST")
        async with client:
            self.session_class_mock.assert_called_with(timeout=mock.ANY)
            client._session.close.assert_not_awaited()
        client._session.close.assert_awaited_with()


class HttpClientMkakerTest(asynctest.TestCase):
    async def setUp(self):
        self._session_mock = CoroutineMock(
            post=CoroutineMock(),
            put=CoroutineMock(),
            delete=CoroutineMock(),
            get=CoroutineMock(),
            close=CoroutineMock(),
        )

    async def test_passes_args_and_kwargs_to_http_client_instance(self):
        url = "https://httpbin.org/ip"
        client_maker = _HttpClientMaker(Mock())

        client_get = client_maker.get(url, 40, 50, timeout=5)
        client_get._session = self._session_mock
        async with client_get:
            self.assertEqual((40, 50), client_get._args)
            self.assertEqual({"timeout": 5}, client_get._kwargs)

    async def test_use_correct_http_method_when_entering_context_get(self):
        url = "https://httpbin.org/ip"
        client_maker = _HttpClientMaker(Mock())

        client_get = client_maker.get(url)
        client_get._session = self._session_mock
        async with client_get:
            client_get._session.get.assert_awaited_with("https://httpbin.org/ip")

    async def test_use_correct_http_method_when_entering_context_post(self):
        url = "https://httpbin.org/ip"
        client_maker = _HttpClientMaker(Mock())

        client_get = client_maker.post(url)
        client_get._session = self._session_mock
        async with client_get:
            client_get._session.post.assert_awaited_with("https://httpbin.org/ip")

    async def test_use_correct_http_method_when_entering_context_put(self):
        url = "https://httpbin.org/ip"
        client_maker = _HttpClientMaker(Mock())

        client_get = client_maker.put(url)
        client_get._session = self._session_mock
        async with client_get:
            client_get._session.put.assert_awaited_with("https://httpbin.org/ip")

    async def test_use_correct_http_method_when_entering_context_delete(self):
        url = "https://httpbin.org/ip"
        client_maker = _HttpClientMaker(Mock())

        client_get = client_maker.delete(url)
        client_get._session = self._session_mock
        async with client_get:
            client_get._session.delete.assert_awaited_with("https://httpbin.org/ip")

    async def test_uses_default_timeout_configs(self):
        self.assertEqual(default_http_client_timeout.connect, 5)
        self.assertEqual(default_http_client_timeout.total, 30)

    async def test_with_block_on_client_return_session(self):
        session_class = Mock(return_value=self._session_mock)
        client_maker = _HttpClientMaker(session_class)

        async with client_maker as session:
            self.assertEqual(session, self._session_mock)

    async def test_reuse_session(self):
        session_class = Mock(return_value=self._session_mock)
        client_maker = _HttpClientMaker(session_class)

        async with client_maker as session1:
            async with client_maker as session2:
                self.assertEqual(session1, self._session_mock)
                self.assertEqual(session2, self._session_mock)
                session_class.assert_called_once()

    async def test_call_session_with_default_timeout_settings(self):
        session_class = Mock(return_value=self._session_mock)
        client_maker = _HttpClientMaker(session_class)

        async with client_maker as session:
            pass
        session_class.assert_called_with(timeout=default_http_client_timeout)
