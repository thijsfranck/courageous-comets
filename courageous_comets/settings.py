import os


class Settings:
    """Shared application configuration."""

    DEBUG = bool(os.environ.get("DEBUG", default=True))
    REDIS_HOST = os.environ["REDIS_HOST"]
    REDIS_PORT = int(os.environ["REDIS_PORT"])
    REDIS_PASSWORD = os.environ["REDIS_PASSWORD"]
