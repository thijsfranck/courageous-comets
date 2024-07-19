import os


class Settings:
    """Shared application configuration."""

    REDIS_HOST = os.environ["REDIS_HOST"]
    REDIS_PORT = int(os.environ["REDIS_PORT"])
    REDIS_PASSWORD = os.environ["REDIS_PASSWORD"]
