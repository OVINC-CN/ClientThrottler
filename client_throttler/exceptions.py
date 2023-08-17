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


class TooManyRequests(Exception):
    """
    Too many requests have reached the limit, and it is set not to delay the request through sleep
    """

    pass


class TooManyRetries(Exception):
    """
    Too many retries have reached the limit.

    Attributes:
        tag -- request tag
        times -- request times
    """

    def __init__(self, tag: str, times: int):
        self.tag = tag
        self.times = times
        message = f"Too many retries have reached the limit, tag: {tag}, times: {times}"
        super().__init__(message)


class TooLongRetries(Exception):
    """
    Too long retries have reached the limit.

    Attributes:
        tag -- request tag
        expect_time -- request expect maximum retry time
        actual_time -- request actual retry time
    """

    def __init__(self, tag: str, expect_time: float, actual_time: float):
        self.expect_time = expect_time
        self.actual_time = actual_time
        message = (
            f"Too long retries have reached the limit, tag: {tag}, "
            f"expect_time: {expect_time}, actual_time: {actual_time}"
        )
        super().__init__(message)


class RateParseError(Exception):
    """
    Rate parse error

    Attributes:
        expression -- input expression that caused the error
        message -- explanation of the error
    """

    def __init__(self, rate: str):
        self.rate = rate
        message = f"Rate parse error, rate: {rate}"
        super().__init__(message)
