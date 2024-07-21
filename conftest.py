from pathlib import Path

import pytest
import yaml

from courageous_comets.nltk import init_nltk
from courageous_comets.transformers import init_transformers


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
