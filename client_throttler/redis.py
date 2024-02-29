# -*- coding: utf-8 -*-
"""
MIT License

Copyright (c) 2023 OVINC-CN

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from redis import Redis


class MockPipeline:
    def __init__(self, client: Redis):
        self._client = client
        self._commands = []

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        return

    def __getattr__(self, func_name):
        return MockCommand(pipeline=self, func_name=func_name)

    def _reset(self):
        self._commands = []

    def execute(self, raise_on_error: bool = True) -> list:
        results = []
        for command in self._commands:
            try:
                result = command.execute()
            except Exception as err:
                result = err
                if raise_on_error:
                    self._reset()
                    raise err
            results.append(result)
        self._reset()
        return results

    def add_command(self, func: "MockCommand") -> None:
        self._commands.append(func)

    def redis_func(self, func_name: str) -> callable:
        return getattr(self._client, func_name)


class MockCommand:
    def __init__(self, pipeline: MockPipeline, func_name: str):
        self.pipeline = pipeline
        self.func = self.pipeline.redis_func(func_name)
        self.args = tuple()
        self.kwargs = dict()

    def __call__(self, *args, **kwargs) -> "MockCommand":
        self.args = args
        self.kwargs = kwargs
        self.pipeline.add_command(self)
        return self

    def execute(self) -> any:
        return self.func(*self.args, **self.kwargs)
