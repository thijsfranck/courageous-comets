import os
from pathlib import Path

import nltk
import pytest
import yaml


@pytest.fixture(scope="session")
def application_config() -> dict:
    """Load the application configuration for testing."""
    with Path("application.yaml").open("r") as file:
        return yaml.safe_load(file)


@pytest.fixture(scope="session", autouse=True)
def _load_nltk_data(application_config: dict) -> None:
    """Load the NLTK data for testing."""
    resources = application_config.get("nltk", [])

    for resource in resources:
        nltk.download(
            resource,
            download_dir=os.getenv("NLTK_DATA_DIR", "nltk_data"),
        )
