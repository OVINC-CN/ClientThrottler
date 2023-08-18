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

import unittest

from client_throttler import Throttler, ThrottlerConfig
from tests.mock.api import request_api
from tests.mock.redis import redis_client
from tests.mock.thread import bulk_request


class ThrottlerTest(unittest.TestCase):
    def test_sleep(self):
        config = ThrottlerConfig(
            func=request_api,
            rate="1/50ms",
            enable_sleep_wait=True,
            redis_client=redis_client,
        )
        bulk_request(Throttler(config), bulk_params=[{} for _ in range(2)])

    def test_no_sleep(self):
        config = ThrottlerConfig(
            func=request_api,
            rate="1/50ms",
            enable_sleep_wait=False,
            redis_client=redis_client,
        )
        bulk_request(Throttler(config), bulk_params=[{} for _ in range(2)])