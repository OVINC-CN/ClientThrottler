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

from redis.exceptions import ConnectionError

from client_throttler import Throttler, ThrottlerConfig
from client_throttler.constants import TimeDurationUnit
from client_throttler.exceptions import RetryTimeout, TooManyRequests, TooManyRetries
from tests.mock.api import request_api
from tests.mock.redis import fake_redis_client, redis_client


class ThrottlerTest(unittest.TestCase):
    class _InMemoryRedisClient:
        def __init__(self):
            self._sorted_sets = {}

        def _get_zset(self, key):
            return self._sorted_sets.setdefault(key, {})

        def ping(self, **kwargs):
            return True

        def zremrangebyscore(self, key, min_score, max_score):
            zset = self._sorted_sets.get(key, {})
            to_delete = [
                member
                for member, score in zset.items()
                if min_score <= score <= max_score
            ]
            for member in to_delete:
                zset.pop(member, None)
            return len(to_delete)

        def zadd(self, key, mapping):
            zset = self._get_zset(key)
            added = 0
            for member, score in mapping.items():
                if member not in zset:
                    added += 1
                zset[member] = score
            return added

        def zcard(self, key):
            return len(self._sorted_sets.get(key, {}))

        def expire(self, key, timeout):
            return True

        def zrem(self, key, member):
            zset = self._sorted_sets.get(key, {})
            return int(zset.pop(member, None) is not None)

        def zrangebyscore(
            self,
            key,
            min_score,
            max_score,
            start=0,
            num=None,
            withscores=False,
        ):
            zset = self._sorted_sets.get(key, {})
            items = [
                (member, score)
                for member, score in zset.items()
                if min_score <= score <= max_score
            ]
            items.sort(key=lambda item: item[1])
            if start:
                items = items[start:]
            if num is not None:
                items = items[:num]
            if withscores:
                return items
            return [member for member, _ in items]

        def delete(self, key):
            return int(self._sorted_sets.pop(key, None) is not None)

        def get_members(self, key):
            return dict(self._sorted_sets.get(key, {}))

    def test_sleep(self):
        config = ThrottlerConfig(
            func=request_api,
            rate="1/50ms",
            enable_sleep_wait=True,
            redis_client=redis_client,
        )
        for _ in range(2):
            Throttler(config)()

    def test_no_sleep(self):
        config = ThrottlerConfig(
            func=request_api,
            rate="1/50ms",
            enable_sleep_wait=False,
            redis_client=redis_client,
        )
        with self.assertRaises(TooManyRequests):
            for _ in range(2):
                Throttler(config)()

    def test_max_request_time(self):
        config = ThrottlerConfig(
            func=request_api,
            rate="1/50ms",
            max_retry_times=1,
            redis_client=redis_client,
        )
        with self.assertRaises(TooManyRetries):
            for _ in range(3):
                Throttler(config)()

    def test_max_retry_duration(self):
        config = ThrottlerConfig(
            func=request_api,
            rate="1/50ms",
            max_retry_duration=0.01,
            redis_client=redis_client,
        )
        with self.assertRaises(RetryTimeout):
            for _ in range(3):
                Throttler(config)()

    def test_clean(self):
        config = ThrottlerConfig(func=request_api, redis_client=redis_client)
        Throttler(config).reset()

    def test_sleep_without_pipeline(self):
        config = ThrottlerConfig(
            func=request_api,
            rate="1/50ms",
            enable_sleep_wait=True,
            redis_client=redis_client,
            enable_pipeline=False,
        )
        for _ in range(2):
            Throttler(config)()

    def test_error_without_pipeline(self):
        config = ThrottlerConfig(
            func=request_api,
            rate="1/50ms",
            enable_sleep_wait=True,
            redis_client=fake_redis_client,
            enable_pipeline=False,
        )
        with self.assertRaises(ConnectionError):
            Throttler(config)()

    def test_no_sleep_without_pipeline(self):
        config = ThrottlerConfig(
            func=request_api,
            rate="1/50ms",
            enable_sleep_wait=False,
            redis_client=redis_client,
            enable_pipeline=False,
        )
        with self.assertRaises(TooManyRequests):
            for _ in range(2):
                Throttler(config)()

    def test_max_request_time_without_pipeline(self):
        config = ThrottlerConfig(
            func=request_api,
            rate="1/50ms",
            max_retry_times=1,
            redis_client=redis_client,
            enable_pipeline=False,
        )
        with self.assertRaises(TooManyRetries):
            for _ in range(3):
                Throttler(config)()

    def test_max_retry_duration_without_pipeline(self):
        config = ThrottlerConfig(
            func=request_api,
            rate="1/50ms",
            max_retry_duration=0.01,
            redis_client=redis_client,
            enable_pipeline=False,
        )
        with self.assertRaises(RetryTimeout):
            for _ in range(3):
                Throttler(config)()

    def test_placeholder_auto_cleanup_without_manual_update(self):
        redis_client = self._InMemoryRedisClient()
        config = ThrottlerConfig(
            func=request_api,
            rate="2/2s",
            redis_client=redis_client,
            enable_pipeline=False,
            placeholder_offset=TimeDurationUnit.MINUTE.value,
        )
        throttler = Throttler(config)

        first_tag = "first-placeholder"
        now = 1000.0
        start_time = now - throttler.config.interval
        self.assertEqual(1, throttler.get_request_count(start_time, first_tag, now))

        future_now = (
            now
            + throttler.config.interval
            + throttler.config.placeholder_offset
            + TimeDurationUnit.MILLISECOND.value
        )
        future_start = future_now - throttler.config.interval
        throttler.get_request_count(future_start, "second-placeholder", future_now)

        members = throttler.config.redis_client.get_members(throttler.config.cache_key)
        self.assertNotIn(first_tag, members)
