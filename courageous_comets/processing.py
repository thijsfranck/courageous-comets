import asyncio
import logging

import discord
from redis.asyncio import Redis

from courageous_comets import preprocessing
from courageous_comets.models import MessageAnalysis
from courageous_comets.redis import messages
from courageous_comets.sentiment import calculate_sentiment
from courageous_comets.vectorizer import Vectorizer
from courageous_comets.words import tokenize_sentence, word_frequency

logger = logging.getLogger(__name__)


async def process_message(
    message: discord.Message,
    *,
    redis: Redis,
    vectorizer: Vectorizer,
) -> str | None:
    """
    Process a message and save it to Redis.

    The following steps are taken to process the message:

    - Clean the message content.
    - Encode the message content.
    - Calculate the sentiment of the message.
    - Tokenize the message content.

    Parameters
    ----------
    message : discord.Message
        The message to process.
    redis : Redis
        The Redis connection.
    vectorizer : Vectorizer
        The vectorizer to use for encoding the message.

    Returns
    -------
    str | None
        The id of the saved message or None if the message was ignored
    """
    if not message.guild:
        return logger.debug(
            "Ignoring message %s because it's not in a guild",
            message.id,
        )

    text = preprocessing.process(message.clean_content)

    if not text:
        return logger.debug(
            "Ignoring message %s because it's empty after processing",
            message.id,
        )

    embedding, sentiment, tokens = await asyncio.gather(
        vectorizer.aencode(text),
        asyncio.to_thread(calculate_sentiment, text),
        asyncio.to_thread(tokenize_sentence, text),
    )

    return await messages.save_message(
        redis,
        MessageAnalysis(
            user_id=str(message.author.id),
            message_id=str(message.id),
            channel_id=str(message.channel.id),
            guild_id=str(message.guild.id),
            timestamp=message.created_at,
            embedding=embedding,
            sentiment=sentiment,
            tokens=word_frequency(tokens),
        ),
    )
