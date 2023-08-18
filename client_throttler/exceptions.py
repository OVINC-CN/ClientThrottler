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


class SDKException(Exception):
    error_code = "sdk_exception"
    error_message = "Unknown Error"

    def __init__(self, error_message=None, error_code=None, *args, **kwargs):
        if error_message is not None:
            self.error_message = error_message
        if error_code is not None:
            self.error_code = error_code

    def __str__(self) -> str:
        return f"[{self.error_code}] {self.error_message}"


class TooManyRequests(SDKException):
    error_code = "too_many_request"
    error_message = "too many requests have reached the limit, and it is set not to delay the request through sleep"


class TooManyRetries(SDKException):
    error_code = "too_many_retry"
    error_message = (
        "too many retries have reached the limit, tag: {tag}, times: {times}"
    )

    def __init__(self, tag, times, error_message=None, error_code=None):
        super().__init__(error_message, error_code)
        self.tag = tag
        self.times = times
        self.error_message = self.error_message.format(tag=tag, times=times)


class RetryTimeout(SDKException):
    error_code = "retry_timeout"
    error_message = (
        "retry duration have reached the limit, "
        "tag: {tag}, expect_time: {expect_time}, actual_time: {actual_time}"
    )

    def __init__(
        self,
        tag: str,
        expect_time: float,
        actual_time: float,
        error_message=None,
        error_code=None,
    ):
        super().__init__(error_message, error_code)
        self.tag = tag
        self.expect_time = expect_time
        self.actual_time = actual_time
        self.error_message = self.error_message.format(
            tag=tag, expect_time=expect_time, actual_time=actual_time
        )


class RateParseError(SDKException):
    error_code = "rate_parse_error"
    error_message = "rate parse error, rate: {rate}"

    def __init__(self, rate: str, error_message=None, error_code=None):
        super().__init__(error_message, error_code)
        self.rate = rate
        self.error_message = self.error_message.format(rate=rate)
