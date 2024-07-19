import asyncio
import sys

from redis.asyncio import ConnectionError, Redis

from courageous_comets import logger
from courageous_comets.error import CourageousCometsError
from courageous_comets.settings import Settings


async def init_redis() -> Redis:
    """Initialize the Redis connection."""
    logger.debug("Connecting to Redis...")

    instance = Redis(
        host="",
        port=Settings.REDIS_PORT,
        password=Settings.REDIS_PASSWORD,
    )

    try:
        await instance.ping()
    except ConnectionError as e:
        message = f"Could not connect to Redis at {Settings.REDIS_HOST}:{Settings.REDIS_PORT}"
        raise CourageousCometsError(message) from e

    logger.info(
        "Connected to Redis at %s:%s",
        Settings.REDIS_HOST,
        Settings.REDIS_PORT,
    )

    return instance


async def main() -> None:
    """Start the appication."""
    redis = await init_redis()

    try:
        logger.info("Starting the Discord client...")
    finally:
        logger.debug("Closing Redis connection...")
        await redis.aclose()
        logger.info("Application shutdown complete.")


try:
    asyncio.run(main())
except CourageousCometsError as e:
    logger.critical(e)
    sys.exit(1)
