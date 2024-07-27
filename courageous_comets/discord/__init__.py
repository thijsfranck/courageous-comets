import asyncio

from courageous_comets import settings

# Limit the number of concurrent requests to the Discord API.
SEMAPHORE = asyncio.Semaphore(settings.DISCORD_API_CONCURRENCY)

__all__ = ["SEMAPHORE"]
