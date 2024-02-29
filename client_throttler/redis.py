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
        self.client = client
        self.results = []

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.clear()

    def execute(self, raise_on_error: bool = True) -> list:
        if raise_on_error:
            for result in self.results:
                if isinstance(result, Exception):
                    raise result
        results = self.results
        self.clear()
        return results

    def clear(self):
        self.results = []

    def __getattr__(self, item):
        return MockFunc(pipeline=self, item=item)


class MockFunc:
    def __init__(self, pipeline: MockPipeline, item: str):
        self.pipeline = pipeline
        self.func = getattr(pipeline.client, item)

    def __call__(self, *args, **kwargs):
        try:
            result = self.func(*args, **kwargs)
        except Exception as e:
            result = e
        self.pipeline.results.append(result)
