import asyncio
import logging
import sys

import discord
import nltk
import redis.asyncio as redis
import yaml
from redisvl.index import AsyncSearchIndex

from courageous_comets import bot, exceptions, settings
from courageous_comets.redis import schema


async def download_nltk_resource(resource: str, download_dir: str) -> None:
    """Download an NLTK resource to the specified directory."""
    logging.debug("Downloading NLTK resource '%s'...", resource)
    try:
        await asyncio.to_thread(
            nltk.download,
            resource,
            download_dir=download_dir,
            quiet=True,
            raise_on_error=True,
        )
    except ValueError as e:
        message = f"Invalid NLTK resource '{resource}'"
        raise exceptions.NltkInitializationError(message) from e


async def init_nltk() -> None:
    """
    Ensure all required NLTK resources are downloaded.

    Downloads the resources specified in the bot configuration file.
    """
    with settings.BOT_CONFIG_PATH.open("r") as file:
        config = yaml.safe_load(file)

    resources = config.get("nltk", [])

    download_tasks = [
        download_nltk_resource(resource, settings.NLTK_DATA_DIR) for resource in resources
    ]

    await asyncio.gather(*download_tasks)

    logging.info("NLTK resources downloaded")


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
    logging.debug("Connecting to Redis...")

    instance = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
    )

    try:
        await instance.ping()
    except redis.AuthenticationError as e:
        message = "Redis authentication failed. Check the REDIS_PASSWORD environment variable."
        raise exceptions.AuthenticationError(message) from e
    except redis.RedisError as e:
        message = f"Could not connect to Redis at {settings.REDIS_HOST}:{settings.REDIS_PORT}"
        raise exceptions.DatabaseConnectionError(message) from e

    logging.info(
        "Connected to Redis at %s:%s",
        settings.REDIS_HOST,
        settings.REDIS_PORT,
    )

    return instance


async def create_indexes(redis: redis.Redis) -> None:
    """Create search indexes on Redis."""
    logging.debug("Creating indexes on redis...")
    message_index = AsyncSearchIndex.from_dict(schema.MESSAGE_SCHEMA)
    message_index.set_client(redis)
    await message_index.create(overwrite=True)


async def main() -> None:
    """
    Start the appication.

    Handles the setup and teardown of the Discord client and Redis connection.
    If a critical error occurs, attempt to shut down gracefully.

    Raises
    ------
    courageous_comets.exceptions.AuthenticationError
        If the Discord token is not valid.
    """
    logging.info("Starting the Courageous Comets application ☄️")

    await init_nltk()
    redis = await init_redis()
    # Create the search indexes on Redis
    await create_indexes(redis)

    try:
        logging.info("Starting the Discord client 🚀")
        await bot.start(settings.DISCORD_TOKEN)
    except discord.LoginFailure as e:
        message = "Discord login failed. Check the DISCORD_TOKEN environment variable."
        raise exceptions.AuthenticationError(message) from e
    finally:
        logging.info("Shutting down gracefully...")
        logging.debug("Closing Redis connection...")
        await redis.aclose()
        logging.info("Application shutdown complete. Goodbye! 👋")


try:
    asyncio.run(main())
except (exceptions.CourageousCometsError, discord.DiscordException) as e:
    logging.critical(
        "A fatal error occurred while running the bot.",
        exc_info=e,
    )
    sys.exit(1)
