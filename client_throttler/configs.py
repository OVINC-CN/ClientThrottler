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

from dataclasses import dataclass
from typing import Tuple, Union

from redis import Redis

from client_throttler.constants import (
    CACHE_KEY_FORMAT,
    RATE_PATTERN,
    Defaults,
    TimeDurationUnit,
)
from client_throttler.exceptions import RateParseError


@dataclass(kw_only=True)
class ThrottlerConfig:
    """
    Configuration for throttler.

    :param rate: The rate limit string
        eg: 1/s, 100/min, 20/5s, period should be one of: ('ms', 'msec', 's', 'sec', 'm', 'min')
    :param prefix: Prefix for the key
    :param key: A str or function that returns the key for the rate-limited method
    :param enable_sleep_wait: Whether to sleep and wait for retry after being rate-limited
    :param max_retry_times: Max retry time of request
    :param max_retry_duration: Max retry duration of request (seconds)
    :param redis_client: Redis Client
    """

    # user params
    rate: str = Defaults.rate
    key_prefix: str = ""
    key: Union[callable, str] = None
    enable_sleep_wait: bool = True
    max_retry_times: int = None
    max_retry_duration: float = None
    redis_client: Redis = None

    # auto registry
    func: callable = None
    max_requests: int = int()
    interval: float = float()

    def __post_init__(self):
        self.max_requests, self.interval = self.parse_rate(self.rate)

    @property
    def cache_key(self) -> str:
        if callable(self.key):
            key = self.key()
        elif self.key:
            key = self.key
        else:
            key = f"{self.func.__module__}.{self.func.__qualname__}"
        return CACHE_KEY_FORMAT.format(f"{self.key_prefix}:{key}")

    def parse_rate(self, rate: str) -> Tuple[int, float]:
        """
        Given the request rate string, return a two tuple of:
        <max_requests>, <period in seconds>
        """

        match = RATE_PATTERN.match(rate)

        if not match:
            raise RateParseError(rate)

        max_requests = int(match.group(1))
        value = float(match.group(2) or Defaults.unit_value)
        try:
            unit = TimeDurationUnit.get_unit_value(match.group(3))
        except ValueError:
            raise RateParseError(rate)
        return max_requests, value * unit


def setup(config: ThrottlerConfig):
    """
    Configure the default params
    """

    global default_config
    default_config = config


default_config = ThrottlerConfig()
