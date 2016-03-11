# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import json
import platform

import aiohttp

import tinify
from .errors import ConnectionError, Error


class Client(object):
    API_ENDPOINT = 'https://api.tinify.com'
    USER_AGENT = 'Tinify/{0} Python/{1} ({2})'.format(tinify.__version__, platform.python_version(),
                                                      platform.python_implementation())

    def __init__(self, key, app_identifier=None):

        self.key = key
        self.app_identifier = app_identifier


        # Fixme - implement cert handling with aiohttp
        # self.session.verify = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'cacert.pem')

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def close(self):
        pass

    async def request(self, method, url, body=None, header={}):
        session = aiohttp.ClientSession(
            auth=aiohttp.BasicAuth('api', self.key),
            headers=(('user-agent', self.USER_AGENT + ' ' + self.app_identifier if self.app_identifier else self.USER_AGENT),)
        )

        url = url if url.lower().startswith('https://') else self.API_ENDPOINT + url
        params = {}
        if isinstance(body, dict):
            if body:
                params['data'] = json.dumps(body)
                params['headers'] = (('content-type', 'application/json'), )
        elif body:
            params['data'] = body

        try:
            response = await session.request(method, url, **params)
        except Exception as err:
            raise ConnectionError('Connection error', cause=err)
        finally:
            session.close()

        # Do some adjustment to look like Requests like response
        response.content = (await response.content.read()).decode('utf-8')
        response.close()
        response.status_code = response.status
        if 300 > response.status_code >= 200:
            response.ok = True
        else:
            response.ok = False

        count = response.headers.get('compression-count')
        if count:
            tinify.compression_count = int(count)

        if response.ok:
            return response
        else:
            details = None
            try:
                details = json.loads(response.content)
            except Exception as err:
                details = {'message': 'Error while parsing response: {0}'.format(err), 'error': 'ParseError'}
            raise Error.create(details.get('message'), details.get('error'), response.status_code)
