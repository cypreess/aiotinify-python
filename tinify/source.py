# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import tinify
from . import Result, ResultMeta

class Source(object):
    @classmethod
    async def from_file(cls, path):
        if hasattr(path, 'read'):
            return await cls._shrink(path)
        else:
            with open(path, 'rb') as f:
                return await cls._shrink(f.read())

    @classmethod
    async def from_buffer(cls, string):
        return await cls._shrink(string)

    @classmethod
    async def from_url(cls, url):
        return await cls._shrink({ "source": { "url": url } })

    @classmethod
    async def _shrink(cls, obj):
        response = await tinify.get_client().request('POST', '/shrink', obj)
        return cls(response.headers.get('location'))

    def __init__(self, url, **commands):
        self.url = url
        self.commands = commands

    def resize(self, **options):
        return type(self)(self.url, **self._merge_commands(resize=options))

    async def store(self, **options):
        response = await tinify.get_client().request('POST', self.url, self._merge_commands(store=options))
        return ResultMeta(response.headers)

    async def result(self):
        response = await tinify.get_client().request('GET', self.url, self.commands)
        return Result(response.headers, response.content)

    async def to_file(self, path):
        return (await self.result()).to_file(path)

    async def to_buffer(self):
        return (await self.result()).to_buffer()

    def _merge_commands(self, **options):
        commands = type(self.commands)(self.commands)
        commands.update(options)
        return commands
