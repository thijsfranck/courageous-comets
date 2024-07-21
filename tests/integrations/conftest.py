from collections.abc import AsyncGenerator

import pytest
from redis.asyncio import Redis

from courageous_comets import settings
from courageous_comets.redis import init_redis


@pytest.fixture()
async def redis() -> AsyncGenerator[Redis, None]:
    """Acquire a connection to the Redis database with teardown."""
    redis = await init_redis()

    yield redis

    # Delete any keys that were created during the test
    keys_to_delete = [key async for key in redis.scan_iter(f"{settings.REDIS_KEYS_PREFIX}:*")]

    if keys_to_delete:
        await redis.delete(*keys_to_delete)

    await redis.aclose()
