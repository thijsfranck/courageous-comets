"""Shared application configuration."""

import logging
import os
import sys
from pathlib import Path

from discord.utils import setup_logging
from dotenv import load_dotenv

from courageous_comets.exceptions import ConfigurationValueError


def read_bot_config_path() -> Path:
    """
    Read the bot configuration path from the environment.

    Returns
    -------
    pathlib.Path
        The path to the bot configuration file.

    Raises
    ------
    courageous_comets.exceptions.ConfigurationValueError
        If the path does not exist.
    """
    result = Path(os.getenv("BOT_CONFIG_PATH", "application.yaml"))

    if not result.exists():
        raise ConfigurationValueError(
            key="BOT_CONFIG_PATH",
            value=os.getenv("BOT_CONFIG_PATH"),
            reason=f"No file found at path '{result.resolve()}'",
        )

    return result


def read_discord_token() -> str:
    """
    Read the Discord token from the environment.

    Returns
    -------
    str
        The Discord bot token.

    Raises
    ------
    courageous_comets.exceptions.ConfigurationValueError
        If the token is not found
    """
    result = os.getenv("DISCORD_TOKEN", "")

    if not result:
        raise ConfigurationValueError(
            key="DISCORD_TOKEN",
            value=os.getenv("DISCORD_TOKEN"),
            reason="No Discord bot token found. Set the DISCORD_TOKEN environment variable.",
        )

    return result


def read_redis_port() -> int:
    """
    Read the Redis port from the environment.

    Returns
    -------
    int
        The Redis port number.

    Raises
    ------
    courageous_comets.exceptions.ConfigurationValueError
        If the port is not a valid port number.
    """
    try:
        result = int(os.getenv("REDIS_PORT", "6379"))
    except ValueError as e:
        raise ConfigurationValueError(
            key="REDIS_PORT",
            value=os.getenv("REDIS_PORT"),
            reason="Value must be an integer (e.g., 6379)",
        ) from e

    if not (0 <= result <= 65535):  # noqa: PLR2004
        raise ConfigurationValueError(
            key="REDIS_PORT",
            value=result,
            reason="Value must be a valid port number (0-65535)",
        )

    return result


# Load environment variables from a .env file. If the file does not exist, this does nothing.
load_dotenv()

# Let discord.py set up the logging configuration
LOG_LEVEL = logging.getLevelNamesMapping().get(os.getenv("LOG_LEVEL", "INFO"), logging.INFO)
setup_logging(level=LOG_LEVEL)


try:
    DISCORD_TOKEN = read_discord_token()
    BOT_CONFIG_PATH = read_bot_config_path()
    NLTK_DATA_DIR = os.getenv("NLTK_DATA_DIR", "nltk_data")
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = read_redis_port()
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
except ConfigurationValueError as e:
    logging.critical("Cannot start the application due to configuration errors", exc_info=e)
    sys.exit(1)

logging.info("Configuration loaded successfully")
