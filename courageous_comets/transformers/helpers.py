import asyncio
import logging
from pathlib import Path

from sentence_transformers import SentenceTransformer

from courageous_comets import settings

logger = logging.getLogger(__name__)


async def download_transformer(resource: str, semaphore: asyncio.Semaphore) -> None:
    """
    Download a transformer to the specified directory.

    Parameters
    ----------
    resource : str
        The transformer to download.
    semaphore : asyncio.Semaphore
        The semaphore to use for concurrency control.
    """
    logger.debug("Downloading transformer %r...", resource)

    async with semaphore:
        await asyncio.to_thread(
            SentenceTransformer,
            model_name_or_path=resource,
            cache_folder=settings.SENTENCE_TRANSFORMERS_HOME,
        )

    logger.debug("Transformer %r downloaded", resource)


async def init_transformers(resources: list[str]) -> None:
    """
    Ensure all required transformers are downloaded.

    Parameters
    ----------
    resources : list[str]
        The list of transformers to download.
    """
    if not any(resources):
        logger.debug("No transformers to download")
        return

    # Create the Huggingface data directory if it does not exist to avoid a race condition when
    # running multiple download tasks concurrently
    Path(settings.SENTENCE_TRANSFORMERS_HOME).mkdir(parents=True, exist_ok=True)

    semaphore = asyncio.Semaphore(settings.SENTENCE_TRANSFORMERS_CONCURRENCY)
    download_tasks = [download_transformer(resource, semaphore) for resource in resources]

    await asyncio.gather(*download_tasks)

    logger.debug("Transformers downloaded")
