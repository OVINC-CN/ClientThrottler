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

from fnmatch import fnmatch
from typing import Any, Dict, List, Optional, Tuple, Union

from redis.exceptions import ConnectionError

from client_throttler.redis import MockPipeline


class InMemoryRedisClient:
    def __init__(self) -> None:
        self._sorted_sets: Dict[str, Dict[str, float]] = {}

    def _decode(self, value: Any) -> Any:
        if isinstance(value, bytes):
            return value.decode()
        return value

    def _get_zset(self, key: Union[str, bytes]) -> Dict[str, float]:
        return self._sorted_sets.setdefault(self._decode(key), {})

    def ping(self, **kwargs: Any) -> bool:
        return True

    def pipeline(self, transaction: bool = False) -> MockPipeline:
        return MockPipeline(self)

    def zremrangebyscore(
        self, key: Union[str, bytes], min_score: float, max_score: float
    ) -> int:
        zset = self._sorted_sets.get(self._decode(key), {})
        to_delete = [
            member for member, score in zset.items() if min_score <= score <= max_score
        ]
        for member in to_delete:
            zset.pop(member, None)
        return len(to_delete)

    def zadd(
        self, key: Union[str, bytes], mapping: Dict[Union[str, bytes], float]
    ) -> int:
        zset = self._get_zset(key)
        added = 0
        for member, score in mapping.items():
            member = self._decode(member)
            if member not in zset:
                added += 1
            zset[member] = score
        return added

    def zcard(self, key: Union[str, bytes]) -> int:
        return len(self._sorted_sets.get(self._decode(key), {}))

    def expire(self, key: Union[str, bytes], timeout: Any) -> bool:
        return True

    def zrem(self, key: Union[str, bytes], member: Union[str, bytes]) -> int:
        zset = self._sorted_sets.get(self._decode(key), {})
        return int(zset.pop(self._decode(member), None) is not None)

    def zrangebyscore(
        self,
        key: Union[str, bytes],
        min_score: float,
        max_score: float,
        start: int = 0,
        num: Optional[int] = None,
        withscores: bool = False,
    ) -> Union[List[bytes], List[Tuple[bytes, float]]]:
        zset = self._sorted_sets.get(self._decode(key), {})
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
            return [(member.encode(), score) for member, score in items]
        return [member.encode() for member, _ in items]

    def delete(self, *keys: Union[str, bytes]) -> int:
        deleted = 0
        for key in keys:
            deleted += int(self._sorted_sets.pop(self._decode(key), None) is not None)
        return deleted

    def keys(self, pattern: Union[str, bytes]) -> List[bytes]:
        pattern = self._decode(pattern)
        return [
            key.encode() for key in self._sorted_sets.keys() if fnmatch(key, pattern)
        ]


redis_client = InMemoryRedisClient()


class FakeRedisClient:
    def __getattr__(self, name):
        def _raise_connection_error(*args, **kwargs):
            raise ConnectionError

        return _raise_connection_error


fake_redis_client = FakeRedisClient()
