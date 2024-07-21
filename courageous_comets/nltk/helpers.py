import asyncio
import logging
from pathlib import Path

import nltk

from courageous_comets import exceptions, settings

logger = logging.getLogger(__name__)


async def download_nltk_resource(resource: str, semaphore: asyncio.Semaphore) -> None:
    """Download an NLTK resource to the specified directory."""
    async with semaphore:
        logger.debug("Downloading NLTK resource '%s'...", resource)
        try:
            await asyncio.to_thread(
                nltk.download,
                resource,
                download_dir=settings.NLTK_DATA_DIR,
                quiet=True,
                raise_on_error=True,
            )
        except ValueError as e:
            message = f"Invalid NLTK resource '{resource}'"
            raise exceptions.NltkInitializationError(message) from e


async def init_nltk(resources: list[str]) -> None:
    """
    Ensure all required NLTK resources are downloaded.

    Downloads the resources specified in the bot configuration file.
    """
    if not any(resources):
        logger.debug("No NLTK resources to download")
        return

    # Create the NLTK data directory if it does not exist to avoid a race condition when running
    # multiple download tasks concurrently
    Path(settings.NLTK_DATA_DIR).mkdir(parents=True, exist_ok=True)

    semaphore = asyncio.Semaphore(settings.NLTK_DOWNLOAD_CONCURRENCY)
    download_tasks = [download_nltk_resource(resource, semaphore) for resource in resources]

    await asyncio.gather(*download_tasks)

    logger.debug("NLTK resources downloaded")
