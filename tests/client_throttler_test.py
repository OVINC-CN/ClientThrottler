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

from client_throttler import ThrottlerConfig
from client_throttler.exceptions import RateParseError


class TestParseRate(unittest.TestCase):
    def test_parse_rate(self):
        test_cases = [
            ("100/s", (100, 1)),
            ("100/20s", (100, 20)),
            ("100/ms", (100, 0.001)),
            ("100/3m", (100, 180)),
        ]

        for rate_str, expected_output in test_cases:
            with self.subTest(rate_str=rate_str):
                config = ThrottlerConfig(rate=rate_str)
                self.assertEqual(
                    (config.max_requests, config.interval), expected_output
                )

    def test_invalid_rate_string(self):
        invalid_rate_strings = [
            "100",
            "abc",
            "100//s",
            "100/-1s",
            "100/s20",
            "100/20",
        ]

        for rate_str in invalid_rate_strings:
            with self.subTest(rate_str=rate_str):
                with self.assertRaises(RateParseError):
                    _ = ThrottlerConfig(rate=rate_str).interval
