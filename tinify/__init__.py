# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import os
import threading
import sys

class tinify(object):
    def __init__(self, module):
        self._module = module
        self._lock = threading.RLock()

        self._client = None
        self._key = os.environ.get('TINIFY_KEY')
        self._app_identifier = None
        self._compression_count = None

    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, value):
        self._key = value
        self._client = None

    @property
    def app_identifier(self):
        return self._app_identifier

    @app_identifier.setter
    def app_identifier(self, value):
        self._app_identifier = value
        self._client = None

    @property
    def compression_count(self):
        return self._compression_count

    @compression_count.setter
    def compression_count(self, value):
        self._compression_count = value

    def get_client(self):
        if not self._key:
            raise AccountError('Provide an API key with tinify.key = ...')

        if not self._client:
            with self._lock:
                if not self._client:
                    self._client = Client(self._key, self._app_identifier)

        return self._client

    # Delegate to underlying base module.
    def __getattr__(self, attr):
        return getattr(self._module, attr)

    async def validate(self):
        try:
            await self.get_client().request('post', '/shrink')
        except ClientError:
            return True

    def from_file(self, path):
        return Source.from_file(path)

    def from_buffer(self, string):
        return Source.from_buffer(string)

    def from_url(self, url):
        return Source.from_url(url)

# Overwrite current module with singleton object.
tinify = sys.modules[__name__] = tinify(sys.modules[__name__])

from .version import __version__

from .client import Client
from .result_meta import ResultMeta
from .result import Result
from .source import Source
from .errors import *

__all__ = [
    b'Client',
    b'Result',
    b'ResultMeta',
    b'Source',
    b'Error',
    b'AccountError',
    b'ClientError',
    b'ServerError',
    b'ConnectionError'
]
