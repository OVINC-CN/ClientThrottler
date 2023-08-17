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

import re
from datetime import timedelta
from enum import Enum
from types import DynamicClassAttribute

RATE_PATTERN = re.compile(r"^(\d+)/(\d*)(\w+)$")
CACHE_KEY_FORMAT = "client_throttler:{}"
CACHE_KEY_TIMEOUT = timedelta(hours=1)


class Defaults:
    rate = "1/s"
    unit_value = 1


class TimeDurationUnit(Enum):
    """
    Time Duration in Second
    """

    NANOSECOND = 1 / 1000**3, "ns"
    MICROSECOND = 1 / 1000**2, "us"
    MILLISECOND = 1 / 1000, "ms"
    SECOND = 1, "s"
    MINUTE = 60, "m"
    HOUR = 60**2, "h"
    DAY = 24 * 60**2, "d"
    YEAR = 365 * 24 * 60**2, "y"

    def __new__(cls, value: float, name):
        obj = object.__new__(cls)
        obj._value_ = value
        obj._short_name_ = name
        return obj

    @DynamicClassAttribute
    def value(self) -> float:
        return self._value_

    @DynamicClassAttribute
    def name(self) -> str:
        return self._short_name_

    @classmethod
    def get_unit_value(cls, unit_name: str) -> float:
        for unit in cls:
            if unit.name == unit_name:
                return unit.value
        raise ValueError(f"Invalid unit name: {unit_name}")
