import asyncio
import logging

import discord
from asyncache import cached
from cachetools import LRUCache

from courageous_comets import models
from courageous_comets.discord import SEMAPHORE

logger = logging.getLogger(__name__)


async def resolve_messages(
    client: discord.Client,
    messages: list[models.Message],
) -> list[discord.Message]:
    """
    Try and resolve a list of messages from Redis to Discord messages.

    Messages that could not be resolved are not included in the returned list. Messages that have no
    content are also filtered out.

    Parameters
    ----------
    client : discord.Client
        The discord client to use to fetch the messages.
    messages : list[models.Message]
        The messages to resolve.

    Returns
    -------
    list[discord.Message]
        A list of `discord.Message` instances that were found.
    """
    requests = [
        get_message(client, int(message.channel_id), int(message.message_id))
        for message in messages
    ]
    return [
        message
        for message in await asyncio.gather(*requests)
        if message is not None and message.clean_content
    ]


@cached(
    LRUCache(maxsize=256),
    key=lambda _, channel_id, message_id: f"{channel_id}-{message_id}",
)
async def get_message(
    client: discord.Client,
    channel_id: int,
    message_id: int,
) -> discord.Message | None:
    """
    Try and fetch a message from Discord given a `channel_id` and `message_id`.

    Uses a cache to avoid fetching the same message multiple times.

    Parameters
    ----------
    client : discord.Client
        The discord client to use to fetch the message.
    channel_id : int
        The channel id of the message.
    message_id : int
        The message id of the message.

    Returns
    -------
    discord.Message | None
        A `discord.Message` instance if the message was found, else `None`.
    """
    channel = client.get_channel(channel_id)

    if not channel or not isinstance(channel, discord.TextChannel):
        return None

    async with SEMAPHORE:
        logging.debug("Fetching message %s from channel %s", message_id, channel_id)
        resolved_message = await channel.fetch_message(message_id)

    if not resolved_message:
        return None

    return resolved_message
