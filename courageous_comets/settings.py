import os

from courageous_comets.error import CourageousCometsError


class Settings:
    """Shared application configuration."""

    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

    try:
        REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
    except ValueError as e:
        message = f"REDIS_PORT must be an integer, got {os.getenv('REDIS_PORT')}"
        raise CourageousCometsError(message) from e
