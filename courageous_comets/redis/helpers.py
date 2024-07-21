import logging

import redis.asyncio as redis
from redisvl.index import AsyncSearchIndex

from courageous_comets import exceptions, settings
from courageous_comets.redis import schema

logger = logging.getLogger(__name__)


async def create_indexes(redis: redis.Redis) -> None:
    """Create search indexes on Redis."""
    logger.debug("Creating indexes on redis...")

    message_index = AsyncSearchIndex.from_dict(schema.MESSAGE_SCHEMA)
    message_index.set_client(redis)

    await message_index.create(overwrite=True)

    logger.debug("Created indexes on Redis")


async def init_redis() -> redis.Redis:
    """
    Initialize the Redis connection.

    Returns
    -------
    redis.asyncio.Redis
        The Redis connection instance.

    Raises
    ------
    courageous_comets.exceptions.AuthenticationError
        If the Redis password is incorrect.
    courageous_comets.exceptions.DatabaseConnectionError
        If the connection to Redis cannot be established.
    """
    logger.debug("Connecting to Redis...")

    instance = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
        decode_responses=True,
    )

    try:
        await instance.ping()
    except redis.AuthenticationError as e:
        message = "Redis authentication failed. Check the REDIS_PASSWORD environment variable."
        raise exceptions.AuthenticationError(message) from e
    except redis.RedisError as e:
        message = f"Could not connect to Redis at {settings.REDIS_HOST}:{settings.REDIS_PORT}"
        raise exceptions.DatabaseConnectionError(message) from e

    logger.info(
        "Connected to Redis at %s:%s",
        settings.REDIS_HOST,
        settings.REDIS_PORT,
    )

    await create_indexes(instance)

    logger.info("Redis initialization complete")

    return instance
