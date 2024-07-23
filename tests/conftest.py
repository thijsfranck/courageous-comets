from pathlib import Path

import pytest
import yaml

from courageous_comets import settings
from courageous_comets.nltk import init_nltk
from courageous_comets.redis.schema import MESSAGE_SCHEMA
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


@pytest.fixture(autouse=True)
def _patch_redis_keys_prefix(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set the REDIS_KEYS_PREFIX for testing.

    The patch applies the following steps:

    - Append _test to the courageous_comets.settings.REDIS_KEYS_PREFIX
    - Update the names of Redis indexes using courageous_comets.settings.REDIS_KEYS_PREFIX

    """
    settings.REDIS_KEYS_PREFIX = settings.REDIS_KEYS_PREFIX + "_test"
    # MonkeyPatch the name of the Redis index for testing
    monkeypatch.setitem(
        MESSAGE_SCHEMA["index"],
        "prefix",
        f"{settings.REDIS_KEYS_PREFIX}:messages",
    )


@pytest.fixture(scope="session")
def vectorizer() -> Vectorizer:
    """Set up the vectorizer for encoding messages."""
    return Vectorizer()
