from collections.abc import AsyncGenerator
from typing import cast

import pytest
from redis.asyncio import Redis

from courageous_comets import settings
from courageous_comets.client import CourageousCometsBot


@pytest.fixture()
async def bot() -> AsyncGenerator[CourageousCometsBot, None]:
    """Fixture that sets up and tears down the CourageousCometsBot instance."""
    instance = CourageousCometsBot()
    await instance.setup_hook()
    yield instance
    await instance.close()


@pytest.fixture()
async def redis(bot: CourageousCometsBot) -> AsyncGenerator[Redis, None]:
    """Acquire a connection to the Redis database with teardown."""
    instance = cast(Redis, bot.redis)

    yield instance

    # Delete any keys that were created during the test
    keys_to_delete = [key async for key in redis.scan_iter(f"{settings.REDIS_KEYS_PREFIX}:*")]

    if keys_to_delete:
        await redis.delete(*keys_to_delete)

    await redis.aclose()
