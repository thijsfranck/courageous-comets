import asyncio
import logging
import sys

import discord
from redis.asyncio import AuthenticationError, Redis, RedisError

from courageous_comets import settings
from courageous_comets.client import bot
from courageous_comets.error import CourageousCometsError

logger = logging.getLogger(__name__)


async def init_redis() -> Redis:
    """Initialize the Redis connection."""
    logger.debug("Connecting to Redis...")

    instance = Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
    )

    try:
        await instance.ping()
    except AuthenticationError as e:
        message = "Redis authentication failed. Check the password."
        raise CourageousCometsError(message) from e
    except RedisError as e:
        message = f"Could not connect to Redis at {settings.REDIS_HOST}:{settings.REDIS_PORT}"
        raise CourageousCometsError(message) from e

    logger.info(
        "Connected to Redis at %s:%s",
        settings.REDIS_HOST,
        settings.REDIS_PORT,
    )

    return instance


async def main() -> None:
    """Start the appication."""
    # Let discord.py set up the logging configuration
    discord.utils.setup_logging(level=settings.LOG_LEVEL)

    logger.info("Starting the Courageous Comets application ☄️")

    redis = await init_redis()

    try:
        logger.info("Starting the Discord client 🚀")
        await bot.start(settings.DISCORD_TOKEN or "")
    except discord.LoginFailure as e:
        message = "Discord login failed. Check the token."
        raise CourageousCometsError(message) from e
    finally:
        logger.info("Shutting down gracefully...")
        logger.debug("Closing Redis connection...")
        await redis.aclose()
        logger.info("Application shutdown complete. Goodbye! 👋")


try:
    asyncio.run(main())
except (CourageousCometsError, discord.DiscordException) as e:
    logging.critical(
        "A fatal error occurred while running the bot.",
        exc_info=e,
    )
    sys.exit(1)
