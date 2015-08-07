# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import sys
from base64 import b64encode

from tinify import Tinify, Client, AccountError, ClientError, ConnectionError, ServerError
import requests

from . import *

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

class TinifyClientRequestWhenValid(TestHelper):
    def setUp(self):
        super(type(self), self).setUp()
        httpretty.register_uri(httpretty.GET, 'https://api.tinify.com/', **{
          'compression-count': 12
        })

    def test_should_issue_request(self):
        Client('key').request('GET', '/')

        self.assertEqual(self.request.headers['authorization'], 'Basic {0}'.format(
           b64encode(b'api:key').decode('ascii')))

    def test_should_issue_request_with_json_body(self):
        Client('key').request('GET', '/', {'hello': 'world'})

        self.assertEqual(self.request.headers['content-type'], 'application/json')
        self.assertEqual(self.request.body, b'{"hello": "world"}')

    def test_should_issue_request_with_user_agent(self):
        Client('key').request('GET', '/')

        self.assertEqual(self.request.headers['user-agent'], Client.USER_AGENT)

    def test_should_update_compression_count(self):
        Client('key').request('GET', '/')

        self.assertEqual(Tinify.compression_count, 12)

class TinifyClientRequestWhenValidWithAppId(TestHelper):
    def setUp(self):
        super(type(self), self).setUp()
        httpretty.register_uri(httpretty.GET, 'https://api.tinify.com/', **{
          'compression-count': 12
        })

    def test_should_issue_request_with_user_agent(self):
        Client('key', 'TestApp/0.2').request('GET', '/')

        self.assertEqual(self.request.headers['user-agent'], Client.USER_AGENT + ' TestApp/0.2')

class TinifyClientRequestWithTimeout(TestHelper):
    @patch('requests.sessions.Session.request', RaiseException(requests.exceptions.Timeout))
    def test_should_raise_connection_error(self):
        with self.assertRaises(ConnectionError) as context:
            Client('key').request('GET', '/')
        self.assertEqual('Timeout while connecting', str(context.exception))

class TinifyClientRequestWithConnectionError(TestHelper):
    @patch('requests.sessions.Session.request', RaiseException(requests.exceptions.ConnectionError('connection error')))
    def test_should_raise_connection_error(self):
        with self.assertRaises(ConnectionError) as context:
            Client('key').request('GET', '/')
        self.assertEqual('Error while connecting: connection error', str(context.exception))

class TinifyClientRequestWithSomeError(TestHelper):
    @patch('requests.sessions.Session.request', RaiseException(RuntimeError('some error')))
    def test_should_raise_connection_error(self):
        with self.assertRaises(ConnectionError) as context:
            Client('key').request('GET', '/')
        self.assertEqual('Error while connecting: some error', str(context.exception))

class TinifyClientRequestWithServerError(TestHelper):
    def test_should_raise_server_error(self):
        httpretty.register_uri(httpretty.GET, 'https://api.tinify.com/', status=584,
            body='{"error":"InternalServerError","message":"Oops!"}')

        with self.assertRaises(ServerError) as context:
            Client('key').request('GET', '/')
        self.assertEqual('Oops! (HTTP 584/InternalServerError)', str(context.exception))

class TinifyClientRequestWithBadServerResponse(TestHelper):
    def test_should_raise_server_error(self):
        httpretty.register_uri(httpretty.GET, 'https://api.tinify.com/', status=543,
            body='<!-- this is not json -->')

        with self.assertRaises(ServerError) as context:
            Client('key').request('GET', '/')
        if sys.version_info < (3,4):
            msg = 'Error while parsing response: No JSON object could be decoded (HTTP 543/ParseError)'
        else:
            msg = 'Error while parsing response: Expecting value: line 1 column 1 (char 0) (HTTP 543/ParseError)'
        self.assertEqual(msg, str(context.exception))

class TinifyClientRequestWithClientError(TestHelper):
    def test_should_raise_client_error(self):
        httpretty.register_uri(httpretty.GET, 'https://api.tinify.com/', status=492,
            body='{"error":"BadRequest","message":"Oops!"}')

        with self.assertRaises(ClientError) as context:
            Client('key').request('GET', '/')
        self.assertEqual('Oops! (HTTP 492/BadRequest)', str(context.exception))

class TinifyClientRequestWithBadCredentialsResponse(TestHelper):
    def test_should_raise_account_error(self):
        httpretty.register_uri(httpretty.GET, 'https://api.tinify.com/', status=401,
            body='{"error":"Unauthorized","message":"Oops!"}')

        with self.assertRaises(AccountError) as context:
            Client('key').request('GET', '/')
        self.assertEqual('Oops! (HTTP 401/Unauthorized)', str(context.exception))