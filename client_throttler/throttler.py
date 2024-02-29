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

import time
import uuid
from typing import Union

from redis.client import Pipeline

from client_throttler.configs import ThrottlerConfig, default_config
from client_throttler.constants import CACHE_KEY_TIMEOUT, TimeDurationUnit
from client_throttler.exceptions import RetryTimeout, TooManyRequests, TooManyRetries
from client_throttler.redis import MockPipeline


class Throttler:
    """
    Distributed rate limiting based on Redis Used to actively limit a specific call,
    calculate the waiting time for excessive requests, and continue the request after delaying through sleep.

    Previous request information used for throttling is stored in the cache.
    """

    def __init__(self, config: ThrottlerConfig = None):
        self.config = config or default_config
        self.config.mix_config()

    def get_request_count(self, start_time: float, tag: str, now: float) -> int:
        """
        Get the number of requests within the time interval
        :param start_time: Start time
        :param tag: Request tag
        :param now: Current time
        """

        """
        1. Delete data outside the interval
        2. Insert the current record (maximum value is used to prevent the record from being deleted)
        3. Get the number of requests within the current interval to determine if the frequency is exceeded
        4. Set the expiration time for the large key to prevent cold data from occupying space
        """

        with self._get_pipline() as pipe:
            print(pipe)
            pipe.zremrangebyscore(
                self.config.cache_key,
                0,
                start_time - TimeDurationUnit.MILLISECOND.value,
            )
            pipe.zadd(self.config.cache_key, {tag: now + TimeDurationUnit.YEAR.value})
            pipe.zcard(self.config.cache_key)
            pipe.expire(self.config.cache_key, CACHE_KEY_TIMEOUT)
            _, _, count, _ = pipe.execute(False)
        return count

    def get_wait_time(self, start_time: float, now: float, tag: str) -> float:
        """
        Get the wait time
        :param start_time: Start time
        :param now: Current time
        :param tag: Request tag
        :return: Wait time (seconds)
        """

        # If rate-limited, remove the inserted record and calculate the next request time
        # based on the time of the first request in the current interval.

        with self._get_pipline() as pipe:
            pipe.zrem(self.config.cache_key, tag)
            pipe.zrangebyscore(
                self.config.cache_key, start_time, now, start=0, num=1, withscores=True
            )
            _, result = pipe.execute()
        if not result:
            return self.config.interval / 2
        _, last_time = result[0]
        return (last_time + self.config.interval - now) / 2 or self.config.interval / 2

    def update_time(self, tag: str) -> None:
        """
        Update this request's time
        :param tag: Request tag
        """

        # If there is not be limited, update the record to the current timestamp plus buffer time
        # (buffer time is used to simulate the interval between unlocking and the request)

        self.config.redis_client.zadd(self.config.cache_key, {tag: time.time()})

    def try_limit(self, tag: str) -> float:
        """
        Try to limit
        :param tag: Request tag
        :return: Wait time (seconds)
        """

        now = time.time()
        start_time = now - self.config.interval
        count = self.get_request_count(start_time, tag, now)
        if count > self.config.max_requests:
            return self.get_wait_time(start_time, now, tag)
        else:
            self.record_metric(count)
            self.update_time(tag)
            return 0

    def check_retry_times(self, tag: str, retry_times: int) -> None:
        if self.config.max_retry_times and retry_times > self.config.max_retry_times:
            raise TooManyRetries(tag, retry_times)

    def check_retry_duration(
        self, tag: str, start_time: float, wait_time: float
    ) -> None:
        if self.config.max_retry_duration:
            expect_time = start_time + self.config.max_retry_duration
            actual_time = time.time() + wait_time
            if actual_time > expect_time:
                raise RetryTimeout(tag, expect_time, actual_time)

    def wait(self, tag: str) -> None:
        """
        Wait
        :param tag: Request tag
        :return: Wait time (seconds)
        """

        retry_times = 0
        start_time = time.time()
        while True:
            wait_time = self.try_limit(tag)
            if not wait_time:
                break
            retry_times += 1
            self.check_retry_times(tag, retry_times)
            self.check_retry_duration(tag, start_time, wait_time)
            if self.config.enable_sleep_wait:
                time.sleep(wait_time)
                continue
            raise TooManyRequests()

    def reset(self) -> None:
        """
        Clean up the keys stored in Redis.
        """

        self.config.redis_client.delete(self.config.cache_key)

    def record_metric(self, count: int) -> None:
        """
        Record metric
        """

        if not self.config.enable_metric_record:
            return

        now = time.time()
        with self._get_pipline() as pipe:
            pipe.zremrangebyscore(
                self.config.metric_key,
                0,
                now - CACHE_KEY_TIMEOUT.seconds,
            )
            pipe.zadd(self.config.metric_key, {f"{count}:{uuid.uuid1()}": time.time()})
            pipe.expire(self.config.metric_key, CACHE_KEY_TIMEOUT)
            pipe.execute(raise_on_error=False)

    def _get_pipline(self) -> Union[MockPipeline, Pipeline]:
        if self.config.enable_pipeline:
            return self.config.redis_client.pipeline(transaction=False)
        return MockPipeline(self.config.redis_client)

    def __call__(self, *args, **kwargs) -> any:
        tag = str(uuid.uuid1())
        self.wait(tag)
        return self.config.func(*args, **kwargs)
