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

THE SOFTWARE IS PROVIDED "AS IS", Wx3ITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import datetime
import math
import time
from dataclasses import dataclass
from typing import List

from client_throttler.configs import ThrottlerConfig, default_config
from client_throttler.constants import (
    CACHE_KEY_TIMEOUT,
    DATETIME_FORMAT,
    METRIC_KEY_FORMAT,
)


@dataclass
class MetricData:
    """
    Metric Data
    """

    id: str
    metric_key: str
    func: str
    node: str
    count: int
    time: str
    timestamp: float


class MetricManager:
    """
    Manage metric
    """

    def __init__(
        self,
        config: ThrottlerConfig = None,
        start_time: float = None,
        end_time: float = None,
    ):
        """
        :param config: ThrottlerConfig, if not set, default_config will be used
        :param start_time: timestamp(ms) of start time
        :param end_time: timestamp(ms) of end time
        """
        self._load_all = config is None
        self.config = config or default_config
        self.config.mix_config()
        self.end_time = math.ceil(end_time or time.time())
        self.start_time = math.floor(
            start_time or (self.end_time - CACHE_KEY_TIMEOUT.seconds)
        )

    def load_metrics(self) -> List[MetricData]:
        if self._load_all:
            return self.load_all_metrics()
        return self.load_exact_metric(self.config.metric_key)

    def load_all_metrics(self) -> List[MetricData]:
        keys = self.config.redis_client.keys(METRIC_KEY_FORMAT.format("*"))
        metrics = []
        for key in keys:
            metrics.extend(
                self.load_exact_metric(key.decode() if isinstance(key, bytes) else key)
            )
        return metrics

    def load_exact_metric(self, key: str) -> List[MetricData]:
        data = self.config.redis_client.zrange(
            key, self.start_time, self.end_time, withscores=True
        )
        return self.format_metric(key, data)

    def format_metric(self, metric_key: str, data: List[tuple]) -> List[MetricData]:
        metrics = []
        for item in data:
            _, _, func_name = metric_key.split(":")
            member, timestamp = item
            count, uniq_id = member.decode().split(":")
            _, _, _, _, node = uniq_id.split("-")
            metrics.append(
                MetricData(
                    id=uniq_id,
                    metric_key=metric_key,
                    func=func_name,
                    node=node,
                    count=int(count),
                    time=datetime.datetime.fromtimestamp(float(timestamp)).strftime(
                        DATETIME_FORMAT
                    ),
                    timestamp=float(timestamp),
                )
            )
        return metrics

    def reset(self) -> None:
        if self._load_all:
            keys = self.config.redis_client.keys(METRIC_KEY_FORMAT.format("*"))
        else:
            keys = [self.config.metric_key]
        if not keys:
            return
        self.config.redis_client.delete(*keys)
