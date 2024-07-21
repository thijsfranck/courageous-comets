from collections.abc import AsyncGenerator
from pathlib import Path

import pytest
import yaml
from redis.asyncio import Redis

from courageous_comets import settings
from courageous_comets.nltk import init_nltk
from courageous_comets.redis.helpers import init_redis
from courageous_comets.transformers import init_transformers
from courageous_comets.vectorizer import Vectorizer


@pytest.fixture(scope="session")
def application_config() -> dict:
    """Load the application configuration for testing."""
    with Path("application.yaml").open("r") as file:
        return yaml.safe_load(file)


@pytest.fixture(scope="session", autouse=True)
async def _load_nltk_data(application_config: dict) -> None:
    """Load the NLTK data for testing."""
    resources = application_config.get("nltk", [])
    await init_nltk(resources)


@pytest.fixture(scope="session", autouse=True)
async def _load_transformers(application_config: dict) -> None:
    """Load the transformers for testing."""
    transformers = application_config.get("transformers", [])
    await init_transformers(transformers)


@pytest.fixture(scope="session", autouse=True)
def _patch_redis_keys_prefix() -> None:
    """Set the REDIS_KEYS_PREFIX for testing."""
    settings.REDIS_KEYS_PREFIX = settings.REDIS_KEYS_PREFIX + "_test"


@pytest.fixture(scope="session")
async def redis_connection() -> AsyncGenerator[Redis, None]:
    """Acquire a connection to the Redis database."""
    redis = await init_redis()
    yield redis
    await redis.aclose()


@pytest.fixture()
async def redis(redis_connection: Redis) -> AsyncGenerator[Redis, None]:
    """Acquire a connection to the Redis database with teardown after each test."""
    yield redis_connection

    # Delete any existing keys created during the test
    keys_to_delete = [
        key async for key in redis_connection.scan_iter(f"{settings.REDIS_KEYS_PREFIX}:*")
    ]

    if keys_to_delete:
        await redis_connection.delete(*keys_to_delete)


@pytest.fixture(scope="session")
def vectorizer() -> Vectorizer:
    """Set up the vectorizer for encoding messages."""
    return Vectorizer()
