# encoding: utf-8

from unittest import TestCase
from mock import Mock, patch
import mock
import flask
import requests
import json

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
            self.assertEqual(called_headers, "bla")

    @patch.object(requests, 'get')
    def test_add_query_string_from_original_request(self, mock_get):
        with application.test_request_context("/v2/apps?a=b&c=d", method="GET"):
            replay_request(flask.request, "http://marathon:8080")
            self.assertTrue(mock_get.called)
            called_headers = mock_get.call_args[1]['params']
            self.assertEqual(dict(called_headers), {"a": "b", "c": "d"})

    @patch.object(requests, 'get')
    def test_add_original_payload_to_upstream_request(self, mock_get):
        with application.test_request_context("/v2/apps?a=b&c=d", method="GET", data="Request Data"):
            replay_request(flask.request, "http://marathon:8080")
            self.assertTrue(mock_get.called)
            called_headers = mock_get.call_args[1]['data']
            self.assertEqual(called_headers, b"Request Data")

    @patch.object(requests, 'get')
    def test_original_headers_to_upstream_request(self, mock_get):
        with application.test_request_context("/v2/apps", method="GET", headers={"X-Header-A": 42, "X-Header-B": 10}):
            replay_request(flask.request, "http://marathon:8080")
            self.assertTrue(mock_get.called)
            called_headers = mock_get.call_args[1]['headers']
            self.assertEqual(called_headers['X-Header-A'], "42")
            self.assertEqual(called_headers['X-Header-B'], "10")

    @patch.object(requests, 'put')
    def test_remove_some_key_before_replay_put_request(self, mock_put):
        """
        We must remove these keys:
            * version
            * fetch
        When GETting an app, Marathon returns a JSON with these two keys, bus refuses to
        accept a PUT/POST on this same app if these keys are present.
        """
        with application.test_request_context("/v2/apps", method="PUT", data='{"id": "/abc", "version": "0", "fetch": ["a", "b"]}', headers={'Content-Type': 'application/json'}):
            replay_request(flask.request, "http://marathon:8080")
            self.assertTrue(mock_put.called)
            called_data_json = json.loads(mock_put.call_args[1]['data'])
            self.assertFalse('version' in called_data_json)
            self.assertFalse('fetch' in called_data_json)

    @patch.object(requests, 'post')
    def test_remove_some_key_before_replay_post_request(self, mock_post):
        """
        We must remove these keys:
            * version
            * fetch
        When GETting an app, Marathon returns a JSON with these two keys, bus refuses to
        accept a PUT/POST on this same app if these keys are present.
        """
        with application.test_request_context("/v2/apps", method="POST", data='{"id": "/abc", "version": "0", "fetch": ["a", "b"]}', headers={'Content-Type': 'application/json'}):
            #flask.request.is_json = True
            replay_request(flask.request, "http://marathon:8080")
            self.assertTrue(mock_post.called)
            called_data_json = json.loads(mock_post.call_args[1]['data'])
            self.assertFalse('version' in called_data_json)
            self.assertFalse('fetch' in called_data_json)

    @patch.object(requests, 'post')
    def test_no_not_attempt_to_parse_a_non_json_body_post(self, mock_post):
        """
        We must remove these keys:
            * version
            * fetch
        When GETting an app, Marathon returns a JSON with these two keys, bus refuses to
        accept a PUT/POST on this same app if these keys are present.
        """
        with application.test_request_context("/v2/apps//foo/bar/restart", method="POST", data=''):
            replay_request(flask.request, "http://marathon:8080")
            self.assertTrue(mock_post.called)

    @patch.object(requests, 'put')
    def test_no_not_attempt_to_parse_a_non_json_body_put(self, mock_put):
        """
        We must remove these keys:
            * version
            * fetch
        When GETting an app, Marathon returns a JSON with these two keys, bus refuses to
        accept a PUT/POST on this same app if these keys are present.
        """
        with application.test_request_context("/v2/apps//foo/bar/restart", method="PUT", data=''):
            replay_request(flask.request, "http://marathon:8080")
            self.assertTrue(mock_put.called)
