import asyncio

from redis.asyncio import Redis

from courageous_comets import logger
from courageous_comets.settings import Settings


async def main() -> None:
    """Start the appication."""
    logger.debug("connecting to Redis")
    redis = Redis(
        host=Settings.REDIS_HOST,
        port=Settings.REDIS_PORT,
        password=Settings.REDIS_PASSWORD,
    )
    logger.debug("checking Redis connection.")
    await redis.ping()
    try:
        logger.debug("starting bot.")
    finally:
        logger.debug("closing Redis connection.")
        await redis.aclose()
        logger.debug("application shutdown complete.")


asyncio.run(main())
