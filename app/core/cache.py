import asyncio
import time
from copy import deepcopy
from typing import Any, Protocol
from collections.abc import Awaitable, Callable


class CacheBackend(Protocol):

    async def get(self, key: str) -> Any | None: ...

    async def get(self, key: str, value: Any, ttl: int = 300): ...

    async def delete(self, key: str) -> None: ...

    async def delete_prefix(self, key: str) -> None: ...


class MemoryCache:

    def __init__(self):
        self._store: dict[str, tuple[Any, float]] = {}
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Any | None:

        async with self._lock:
            item = self._store.get(key)

            if item is None:
                return None

            value, expires_at = item

            if time.monotonic() >= expires_at:
                del self._store[key]
                return None

            return deepcopy(value)

    async def set(
        self,
        key: str,
        value: Any,
        ttl: int = 300,
    ) -> None:

        if ttl <= 0:
            raise ValueError("Cache TTL must be greater than zero")

        expires_at = time.monotonic() + ttl

        async with self._lock:
            self._store[key] = (deepcopy(value), expires_at)

    async def delete(self, key: str) -> None:

        async with self._lock:
            self._store.pop(key, None)

    async def delete_prefix(self, prefix: str) -> None:

        async with self._lock:
            keys = [key for key in self._store if key.startswith(prefix)]

            for key in keys:
                del self._store[key]

    async def clear(self) -> None:

        async with self._lock:
            self._store.clear()


# Application-wide cache instance
cache: CacheBackend = MemoryCache()


async def invalidate_user_cache(user_id: int) -> None:
    """
    Invalidate all cached data belonging to a particular user.
    """

    await cache.delete_prefix(f"user:{user_id}:")


async def get_or_set(
    key: str,
    factory: Callable[[], Awaitable[Any]],
    ttl: int = 300,
) -> Any:
    return await get_or_set_with_cache(cache, key, factory, ttl)


async def get_or_set_with_cache(
    backend: CacheBackend,
    key: str,
    factory: Callable[[], Awaitable[Any]],
    ttl: int = 300,
) -> Any:
    cached_value = await backend.get(key)

    if cached_value is not None:
        return cached_value

    value = await factory()
    await backend.set(key, value, ttl)

    return value


async def get_or_set(
    key: str,
    factory,
    ttl: int = 300,
):
    return await get_or_set_with_cache(
        cache,
        key,
        factory,
        ttl,
    )
