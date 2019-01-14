# encoding: utf-8

from unittest import TestCase
from mock import Mock, patch
import mock
import flask
import requests
import json
from requests.exceptions import ConnectionError
from responses import RequestsMock
import responses

from hollowman.app import application
from hollowman.upstream import replay_request, _make_request
import hollowman.conf
from tests import RequestStub


class UpstreamTest(TestCase):
    @patch.object(requests, "get")
    def test_replay_request_removes_specific_headers_from_upstream_response(
        self, mock_get
    ):
        HEADER_NAME_CONTENT_ENCODING = "Content-Encoding"
        HEADER_NAME_TRANSFER_ENCODING = "Transfer-Encoding"
        mock_get.return_value = RequestStub(
            headers={
                HEADER_NAME_CONTENT_ENCODING: "gzip",
                HEADER_NAME_TRANSFER_ENCODING: "chunked",
            }
        )
        with application.test_request_context("/v2/apps", method="GET"):
            response = replay_request(flask.request)
            self.assertFalse(
                HEADER_NAME_CONTENT_ENCODING in response.headers.keys()
            )
            self.assertFalse(
                HEADER_NAME_TRANSFER_ENCODING in response.headers.keys()
            )

    @patch.object(requests, "get")
    def test_remove_conent_length_header(self, mock_get):
        with application.test_request_context(
            "/v2/apps", method="GET", headers={"Content-Length": 42}
        ):
            replay_request(flask.request)
            self.assertTrue(mock_get.called)
            called_headers = mock_get.call_args[1]["headers"]
            self.assertTrue("Content-Length" not in called_headers)

    @patch.object(requests, "get")
    def test_remove_conent_length_header_mixed_case(self, mock_get):
        with application.test_request_context(
            "/v2/apps", method="GET", headers={"COntenT-LenGtH": 42}
        ):
            replay_request(flask.request)
            self.assertTrue(mock_get.called)
            called_headers = mock_get.call_args[1]["headers"]
            header_names = [k.lower() for k in called_headers.keys()]
            self.assertTrue("content-length" not in called_headers)

    @patch.object(requests, "get")
    @patch.multiple(hollowman.conf, MARATHON_AUTH_HEADER="bla")
    def test_add_authorization_header(self, mock_get):
        with application.test_request_context("/v2/apps", method="GET"):
            replay_request(flask.request)
            self.assertTrue(mock_get.called)
            called_headers = mock_get.call_args[1]["headers"]["Authorization"]
            self.assertEqual(called_headers, "bla")

    @patch.object(requests, "get")
    def test_add_query_string_from_original_request(self, mock_get):
        with application.test_request_context("/v2/apps?a=b&c=d", method="GET"):
            replay_request(flask.request)
            self.assertTrue(mock_get.called)
            called_headers = mock_get.call_args[1]["params"]
            self.assertEqual(dict(called_headers), {"a": "b", "c": "d"})

    @patch.object(requests, "get")
    def test_add_original_payload_to_upstream_request(self, mock_get):
        with application.test_request_context(
            "/v2/apps?a=b&c=d", method="GET", data="Request Data"
        ):
            replay_request(flask.request)
            self.assertTrue(mock_get.called)
            called_headers = mock_get.call_args[1]["data"]
            self.assertEqual(called_headers, b"Request Data")

    @patch.object(requests, "get")
    def test_original_headers_to_upstream_request(self, mock_get):
        with application.test_request_context(
            "/v2/apps",
            method="GET",
            headers={"X-Header-A": 42, "X-Header-B": 10},
        ):
            replay_request(flask.request)
            self.assertTrue(mock_get.called)
            called_headers = mock_get.call_args[1]["headers"]
            self.assertEqual(called_headers["X-Header-A"], "42")
            self.assertEqual(called_headers["X-Header-B"], "10")

    @patch.object(requests, "put")
    def test_remove_some_key_before_replay_put_request_data_is_a_list(
        self, mock_put
    ):
        """
        A API aceita uma lista se o request for um PUT em /v2/apps.
        O pop() da lista se comporta diferente do pop do dict. Temos que tratar isso.
        """
        with application.test_request_context(
            "/v2/apps",
            method="PUT",
            data='[{"id": "/abc", "version": "0", "fetch": ["a", "b"], "secrets": {}}]',
            headers={"Content-Type": "application/json"},
        ):
            replay_request(flask.request)
            self.assertTrue(mock_put.called)
            called_data_json = json.loads(mock_put.call_args[1]["data"])
            self.assertFalse("version" in called_data_json[0])
            self.assertFalse("fetch" in called_data_json[0])
            self.assertFalse("secrets" in called_data_json[0])

    @patch.object(requests, "put")
    def test_remove_some_key_before_replay_put_request(self, mock_put):
        """
        We must remove these keys:
            * version
            * fetch
        When GETting an app, Marathon returns a JSON with these two keys, bus refuses to
        accept a PUT/POST on this same app if these keys are present.
        """
        with application.test_request_context(
            "/v2/apps",
            method="PUT",
            data='{"id": "/abc", "version": "0", "fetch": ["a", "b"], "secrets": {}}',
            headers={"Content-Type": "application/json"},
        ):
            replay_request(flask.request)
            self.assertTrue(mock_put.called)
            called_data_json = json.loads(mock_put.call_args[1]["data"])
            self.assertFalse("version" in called_data_json)
            self.assertFalse("fetch" in called_data_json)
            self.assertFalse("secrets" in called_data_json)

    @patch.object(requests, "post")
    def test_remove_some_key_before_replay_post_request(self, mock_post):
        """
        We must remove these keys:
            * version
            * fetch
        When GETting an app, Marathon returns a JSON with these two keys, bus refuses to
        accept a PUT/POST on this same app if these keys are present.
        """
        with application.test_request_context(
            "/v2/apps",
            method="POST",
            data='{"id": "/abc", "version": "0", "fetch": ["a", "b"], "secrets": {}}',
            headers={"Content-Type": "application/json"},
        ):
            # flask.request.is_json = True
            replay_request(flask.request)
            self.assertTrue(mock_post.called)
            called_data_json = json.loads(mock_post.call_args[1]["data"])
            self.assertFalse("version" in called_data_json)
            self.assertFalse("fetch" in called_data_json)
            self.assertFalse("secrets" in called_data_json)

    @patch.object(requests, "post")
    def test_no_not_attempt_to_parse_a_non_json_body_post(self, mock_post):
        with application.test_request_context(
            "/v2/apps//foo/bar/restart", method="POST", data=""
        ):
            replay_request(flask.request)
            self.assertTrue(mock_post.called)

    @patch.object(requests, "put")
    def test_no_not_attempt_to_parse_a_non_json_body_put(self, mock_put):
        with application.test_request_context(
            "/v2/apps//foo/bar/restart", method="PUT", data=""
        ):
            replay_request(flask.request)
            self.assertTrue(mock_put.called)

    def test_make_request_raise_exception_if_all_fail(self):
        marathon_addresses = [
            "http://127.0.0.1:8080",
            "http://172.30.0.1:8080",
            "http://172.31.0.1:8080",
        ]
        with RequestsMock() as rsps, patch.multiple(
            hollowman.conf, MARATHON_ADDRESSES=marathon_addresses
        ):
            self.assertRaises(Exception, _make_request, "/v2/apps", "get")

    def test_make_request_return_response_from_first_connectable_host(self):
        """
        O primeiro server que conseguirmos conectar, ou seja, que não lance
        ConnectionError, é a resposta que vamos retornar
        Endpoints atuais:
            http://127.0.0.1:8080 > Invalido
            http://172.30.0.1:8080 > Vallido
            http://172.31.0.1:8080 > Invalido
        """
        marathon_addresses = [
            "http://127.0.0.1:8080",
            "http://172.30.0.1:8080",
            "http://172.31.0.1:8080",
        ]
        with RequestsMock() as rsps, patch.multiple(
            hollowman.conf, MARATHON_ADDRESSES=marathon_addresses
        ), patch.multiple(
            hollowman.conf, MARATHON_LEADER=marathon_addresses[0]
        ):
            rsps.add(
                "GET",
                url=marathon_addresses[1] + "/v2/apps",
                status=200,
                body="OK",
            )
            response = _make_request("/v2/apps", "get")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(b"OK", response.content)

    def test_remove_x_marathon_leader_header_from_upsream_response(self):
        marathon_addresses = ["http://127.0.0.1:8080"]
        with RequestsMock() as rsps, patch.multiple(
            hollowman.conf, MARATHON_ADDRESSES=marathon_addresses
        ), patch.multiple(
            hollowman.conf, MARATHON_LEADER=marathon_addresses[0]
        ):
            rsps.add(
                "GET",
                url=marathon_addresses[0] + "/v2/apps",
                status=200,
                body="OK",
                headers={"X-Marathon-Leader": marathon_addresses[0]},
            )
            response = _make_request("/v2/apps", "get")
            self.assertEqual(response.status_code, 200)
            self.assertTrue("x-marathon-leader" not in response.headers.keys())

    def test_make_request_update_new_marathon_leader(self):
        marathon_addresses = [
            "http://172.29.0.1:8080",
            "http://172.30.0.1:8080",
        ]
        with RequestsMock() as rsps, patch.multiple(
            hollowman.conf, MARATHON_ADDRESSES=marathon_addresses
        ), patch.multiple(
            hollowman.conf, MARATHON_LEADER=marathon_addresses[0]
        ):
            rsps.add(
                "GET",
                url=marathon_addresses[0] + "/v2/apps",
                status=200,
                body="OK",
                headers={"X-Marathon-Leader": marathon_addresses[1]},
            )
            response = _make_request("/v2/apps", "get")
            self.assertEqual(
                hollowman.conf.MARATHON_LEADER, marathon_addresses[1]
            )

    def test_make_request_call_leader_first(self):
        """
        Sempre chamamos prmeiro o IP do lider que conhecemos
        """
        marathon_addresses = [
            "http://invalid-host:8080",
            "http://172.30.0.1:8080",
            "http://172.31.0.1:8080",
        ]
        with RequestsMock() as rsps, patch.multiple(
            hollowman.conf, MARATHON_ADDRESSES=marathon_addresses
        ), patch.multiple(
            hollowman.conf, MARATHON_LEADER=marathon_addresses[2]
        ):
            rsps.add(
                "GET",
                url=marathon_addresses[2] + "/v2/apps",
                status=200,
                body="OK",
            )
            try:
                response = _make_request("/v2/apps", "get")
            except Exception as e:
                self.fail(
                    "Não deveria ter tentado conectar nos hosts invalidos"
                )
            self.assertEqual(b"OK", response.content)
