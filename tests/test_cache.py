import asyncio
import pytest

from app.core.cache import (
    MemoryCache,
    get_or_set_with_cache,
)


def test_cache_set_and_get():

    async def run_test():
        cache = MemoryCache()

        await cache.set("test:key", {"amount": 500})

        result = await cache.get("test:key")

        assert result == {"amount": 500}

    asyncio.run(run_test())


def test_cache_returns_none_for_missing_key():

    async def run_test():
        cache = MemoryCache()

        result = await cache.get("missing:key")

        assert result is None

    asyncio.run(run_test())


def test_cache_expiration():

    async def run_test():
        cache = MemoryCache()

        await cache.set("test:key", "value", ttl=1)

        assert await cache.get("test:key") == "value"

        await asyncio.sleep(1.1)

        assert await cache.get("test:key") is None

    asyncio.run(run_test())


def test_cache_delete():

    async def run_test():
        cache = MemoryCache()

        await cache.set("test:key", "value")

        await cache.delete("test:key")

        assert await cache.get("test:key") is None

    asyncio.run(run_test())


def test_cache_delete_prefix():

    async def run_test():
        cache = MemoryCache()

        await cache.set("user:1:summary", {"balance": 500})
        await cache.set("user:1:analytics", {"income": 1000})
        await cache.set("user:2:summary", {"balance": 200})

        await cache.delete_prefix("user:1:")

        assert await cache.get("user:1:summary") is None
        assert await cache.get("user:1:analytics") is None

        assert await cache.get("user:2:summary") == {"balance": 200}

    asyncio.run(run_test())


def test_cache_rejects_invalid_ttl():

    async def run_test():
        cache = MemoryCache()

        with pytest.raises(ValueError):
            await cache.set("test:key", "value", ttl=0)

    asyncio.run(run_test())


def test_cache_returns_independent_copy():

    async def run_test():
        cache = MemoryCache()

        original = {"amount": 500}

        await cache.set("test:key", original)

        result = await cache.get("test:key")
        result["amount"] = 1000

        assert await cache.get("test:key") == {"amount": 500}

    asyncio.run(run_test())


def test_get_or_set_caches_result():
    async def run_test():
        test_cache = MemoryCache()
        calls = 0

        async def factory():
            nonlocal calls
            calls += 1
            return {"income": 5000, "expenses": 2000}

        first = await get_or_set_with_cache(test_cache, "summary:1", factory)
        second = await get_or_set_with_cache(test_cache, "summary:1", factory)

        assert first == second
        assert calls == 1

    asyncio.run(run_test())
