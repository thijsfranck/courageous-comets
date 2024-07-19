"""Shared application configuration."""

import logging
import os

from dotenv import load_dotenv

from courageous_comets.error import CourageousCometsError

load_dotenv()

BOT_CONFIG_PATH = os.getenv("BOT_CONFIG_PATH", "application.yaml")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
LOG_LEVEL = logging.getLevelNamesMapping().get(os.getenv("LOG_LEVEL", "INFO"), logging.INFO)
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

try:
    REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
except ValueError as e:
    message = f"REDIS_PORT must be an integer, got {os.getenv('REDIS_PORT')}"
    raise CourageousCometsError(message) from e
