# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from base64 import b64encode

import tinify
from . import *

Tinify = tinify.Tinify

class TinifyKey(TestHelper):
    def test_should_reset_client_with_new_key(self):
        httpretty.register_uri(httpretty.GET, 'https://api.tinify.com/')
        tinify.set_key('abcde')
        Tinify.client
        tinify.set_key('fghij')
        Tinify.client.request('GET', '/')
        self.assertEqual(self.request.headers['authorization'], 'Basic {}'.format(
           b64encode(b'api:fghij').decode('ascii')))

class TinifyClient(TestHelper):
    def test_with_key_should_return_client(self):
        tinify.set_key('abcde')
        self.assertIsInstance(Tinify.client, tinify.Client)

    def test_without_key_should_raise_error(self):
        with self.assertRaises(tinify.AccountError):
            Tinify.client

class TinifyValidate(TestHelper):
    def test_with_valid_key_should_return_true(self):
        httpretty.register_uri(httpretty.POST, 'https://api.tinify.com/shrink', status=400,
            body='{"error":"InputMissing","message":"No input"}')
        tinify.set_key('valid')
        self.assertEqual(True, tinify.validate())

    def test_with_error_should_raise_error(self):
        httpretty.register_uri(httpretty.POST, 'https://api.tinify.com/shrink', status=401,
            body='{"error":"Unauthorized","message":"Credentials are invalid"}')
        tinify.set_key('valid')
        with self.assertRaises(tinify.AccountError):
            tinify.validate()

class TinifyFromBuffer(TestHelper):
    def test_should_return_source(self):
        httpretty.register_uri(httpretty.POST, 'https://api.tinify.com/shrink',
            location='https://api.tinify.com/some/location')
        tinify.set_key('valid')
        self.assertIsInstance(tinify.from_buffer('png file'), tinify.Source)

class TinifyFromFile(TestHelper):
    def test_should_return_source(self):
        httpretty.register_uri(httpretty.POST, 'https://api.tinify.com/shrink',
            location='https://api.tinify.com/some/location')
        tinify.set_key('valid')
        self.assertIsInstance(tinify.from_file(dummy_file), tinify.Source)