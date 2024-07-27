"""Shared application configuration."""

import logging
import os
import sys
import warnings
from pathlib import Path

import coloredlogs
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


def read_int(key: str, default: int) -> int:
    """
    Read an integer value from the environment.

    Parameters
    ----------
    key : str
        The environment variable key.
    default : int
        The default value to use if the environment variable is not set.

    Returns
    -------
    int
        The integer value.

    Raises
    ------
    courageous_comets.exceptions.ConfigurationValueError
        If the value is not a valid integer.
    """
    try:
        result = int(os.getenv(key, str(default)))
    except ValueError as e:
        raise ConfigurationValueError(
            key=key,
            value=os.getenv(key),
            reason="Value must be an integer",
        ) from e

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
    result = read_int("REDIS_PORT", 6379)

    if not (0 <= result <= 65535):  # noqa: PLR2004
        raise ConfigurationValueError(
            key="REDIS_PORT",
            value=result,
            reason="Value must be a valid port number (0-65535)",
        )

    return result


def setup_logging() -> None:
    """Set up logging for the application."""
    coloredlogs.install(
        level=LOG_LEVEL,
        fmt="{asctime} {levelname:<8} [{name}] {message}",
        datefmt="%Y-%m-%d %H:%M:%S",
        style="{",
        reconfigure=True,
    )


# Load environment variables from a .env file. If the file does not exist, this does nothing.
load_dotenv()

# Suppress warnings from libraries
warnings.filterwarnings("ignore")

# Set up logging for the application
LOG_LEVEL = logging.getLevelNamesMapping().get(
    os.getenv("LOG_LEVEL", "INFO"),
    logging.INFO,
)

setup_logging()

# Determine whether the application is running in a development environment
IS_DEV = os.getenv("ENVIRONMENT", "production") == "development"

if IS_DEV:
    logging.warning("🚨 Application is running in development mode! 🚨")

# Load configuration values from the environment
try:
    DISCORD_TOKEN = read_discord_token()
    BOT_CONFIG_PATH = read_bot_config_path()
    DISCORD_API_CONCURRENCY = read_int("DISCORD_API_CONCURRENCY", 3)
    NLTK_DATA_DIR = os.getenv("NLTK_DATA", "nltk_data")
    NLTK_DOWNLOAD_CONCURRENCY = read_int("NLTK_DOWNLOAD_CONCURRENCY", 3)
    PREPROCESSING_MAX_WORD_LENGTH = read_int("MAX_WORD_LENGTH", 35)
    PREPROCESSING_MESSAGE_TRUNCATE_LENGTH = read_int("TRUNCATE_LENGTH", 256)
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = read_redis_port()
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
    REDIS_KEYS_PREFIX = os.getenv("REDIS_KEYS_PREFIX", "courageous_comets")
    # Maximum number of items to return from a query
    QUERY_LIMIT = read_int("QUERY_LIMIT", 10)
    # Huggingface environment variable for caching downloaded models.
    # https://huggingface.co/docs/huggingface_hub/v0.24.0/package_reference/environment_variables#hf_home
    HF_HOME = os.getenv(
        "HF_HOME",
        "hf_data",
    )
    HF_DOWNLOAD_CONCURRENCY = read_int("HF_DOWNLOAD_CONCURRENCY", 3)
except ConfigurationValueError as e:
    logging.critical(
        "Cannot start the application due to configuration errors",
        exc_info=e,
    )
    sys.exit(1)

logging.info("Configuration loaded successfully")
