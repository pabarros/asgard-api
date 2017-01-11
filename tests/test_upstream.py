# encoding: utf-8

from unittest import TestCase
from mock import Mock, patch
import mock
import flask
import requests

from hollowman.app import application
from hollowman.upstream import replay_request
import hollowman.conf


class UpstreamTest(TestCase):

    @patch.object(requests, 'get')
    def test_remove_conent_length_header(self, mock_get):
        with application.test_request_context("/v2/apps", method="GET", headers={"Content-Length": 42}):
            replay_request(flask.request, "http://marathon:8080")
            self.assertTrue(mock_get.called)
            called_headers = mock_get.call_args[1]['headers']
            self.assertTrue('Content-Length' not in called_headers)

    @patch.object(requests, 'get')
    def test_remove_conent_length_header_mixed_case(self, mock_get):
        with application.test_request_context("/v2/apps", method="GET", headers={"COntenT-LenGtH": 42}):
            replay_request(flask.request, "http://marathon:8080")
            self.assertTrue(mock_get.called)
            called_headers = mock_get.call_args[1]['headers']
            header_names = [k.lower() for k in called_headers.keys()]
            self.assertTrue('content-length' not in called_headers)

    @patch.object(requests, 'get')
    @patch.multiple(hollowman.conf, MARATHON_AUTH_HEADER="bla")
    def test_add_authorization_header(self, mock_get):
        with application.test_request_context("/v2/apps", method="GET"):
            replay_request(flask.request, "http://marathon:8080")
            self.assertTrue(mock_get.called)
            called_headers = mock_get.call_args[1]['headers']['Authorization']
            self.assertEquals(called_headers, "bla")

    @patch.object(requests, 'get')
    def test_add_query_string_from_original_request(self, mock_get):
        with application.test_request_context("/v2/apps?a=b&c=d", method="GET"):
            replay_request(flask.request, "http://marathon:8080")
            self.assertTrue(mock_get.called)
            called_headers = mock_get.call_args[1]['params']
            self.assertEquals(dict(called_headers), {"a": "b", "c": "d"})

    @patch.object(requests, 'get')
    def test_add_original_payload_to_upstream_request(self, mock_get):
        with application.test_request_context("/v2/apps?a=b&c=d", method="GET", data="Request Data"):
            replay_request(flask.request, "http://marathon:8080")
            self.assertTrue(mock_get.called)
            called_headers = mock_get.call_args[1]['data']
            self.assertEquals(called_headers, "Request Data")

    @patch.object(requests, 'get')
    def test_original_headers_to_upstream_request(self, mock_get):
        with application.test_request_context("/v2/apps", method="GET", headers={"X-Header-A": 42, "X-Header-B": 10}):
            replay_request(flask.request, "http://marathon:8080")
            self.assertTrue(mock_get.called)
            called_headers = mock_get.call_args[1]['headers']
            self.assertEquals(called_headers['X-Header-A'], "42")
            self.assertEquals(called_headers['X-Header-B'], "10")
