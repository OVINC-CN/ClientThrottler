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
from functools import cached_property
from typing import Tuple, Union

from redis import Redis

from client_throttler.constants import (
    CACHE_KEY_FORMAT,
    RATE_PATTERN,
    Defaults,
    TimeDurationUnit,
    Unset,
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
    :param func: function that needs throttle, no need when using decorator
    """

    rate: str = Unset()
    key_prefix: str = Unset()
    key: Union[callable, str] = Unset()
    enable_sleep_wait: bool = Unset()
    max_retry_times: int = Unset()
    max_retry_duration: float = Unset()
    redis_client: Redis = Unset()
    func: callable = Unset()

    @cached_property
    def cache_key(self) -> str:
        if callable(self.key):
            key = self.key()
        elif self.key:
            key = self.key
        else:
            key = f"{self.func.__module__}.{self.func.__qualname__}"
        return CACHE_KEY_FORMAT.format(f"{self.key_prefix}:{key}")

    @cached_property
    def max_requests(self) -> int:
        return self.parse_rate(self.rate)[0]

    @cached_property
    def interval(self) -> float:
        return self.parse_rate(self.rate)[1]

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

    def mix_config(
        self, config: "ThrottlerConfig" = None, replace: bool = False
    ) -> None:
        """
        mix default config with custom config
        """

        # if config not set, use default config
        if not config and "default_config" not in globals():
            return

        config = config or default_config

        # replace None with default value
        for key, val in self.__dict__.items():
            # skip already configured and not force replace
            if not isinstance(val, Unset) and not replace:
                continue
            # skip unset default value
            default_val = getattr(config, key, None)
            if isinstance(default_val, Unset):
                continue
            setattr(self, key, default_val)


def setup(config: ThrottlerConfig):
    """
    Configure the default params
    """

    global default_config
    default_config.mix_config(config=config, replace=True)


default_config = ThrottlerConfig(
    rate=Defaults.rate,
    enable_sleep_wait=Defaults.enable_sleep_wait,
)
