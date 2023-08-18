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

from client_throttler import Throttler, ThrottlerConfig, setup
from client_throttler.metrics import MetricManager
from tests.mock.api import request_api
from tests.mock.redis import redis_client


class MetricsTest(unittest.TestCase):
    def test_metric_collect(self):
        config = ThrottlerConfig(
            func=request_api,
            rate="1/50ms",
            enable_metric_record=True,
            redis_client=redis_client,
        )
        Throttler(config)()

    def test_load_metric(self):
        config = ThrottlerConfig(
            func=request_api,
            rate="1/50ms",
            enable_metric_record=True,
            redis_client=redis_client,
        )
        Throttler(config)()
        manager = MetricManager(config)
        _ = manager.load_metrics()
        manager.reset()

        setup(config)
        Throttler(config)()
        manager = MetricManager()
        manager.reset()
        manager.reset()
