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

import datetime
import unittest
import uuid

from client_throttler.exceptions import (
    RateParseError,
    RetryTimeout,
    SDKException,
    TooManyRetries,
)


class ExceptionTest(unittest.TestCase):
    def test_exception(self):
        error_message = "test_exception"
        error_code = "test_exception"
        tag = uuid.uuid1().hex
        times = 1
        rate = "1/ss1"
        expect_time = datetime.datetime.now().timestamp()
        actual_time = datetime.datetime.now().timestamp()
        detail = "[test_exception] test_exception"

        error = SDKException(error_message, error_code)
        self.assertEqual(detail, str(error))

        detail = f"[{TooManyRetries.error_code}] {TooManyRetries.error_message.format(tag=tag, times=times)}"
        error = TooManyRetries(tag=tag, times=times)
        self.assertEqual(detail, str(error))

        detail = (
            f"[{RetryTimeout.error_code}] "
            f"{RetryTimeout.error_message.format(tag=tag, expect_time=expect_time, actual_time=actual_time)}"
        )
        error = RetryTimeout(tag=tag, expect_time=expect_time, actual_time=actual_time)
        self.assertEqual(detail, str(error))

        detail = f"[{RateParseError.error_code}] {RateParseError.error_message.format(rate=rate)}"
        error = RateParseError(rate=rate)
        self.assertEqual(detail, str(error))
