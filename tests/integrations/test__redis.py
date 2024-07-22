import datetime

import pytest_asyncio
from redis.asyncio import Redis

from courageous_comets import models
from courageous_comets.redis.keys import key_schema
from courageous_comets.redis.messages import get_similar_messages, save_message
from courageous_comets.sentiment import calculate_sentiment
from courageous_comets.vectorizer import Vectorizer


@pytest_asyncio.fixture(scope="session")
async def message(vectorizer: Vectorizer) -> models.MessageAnalysis:
    """Fixture that sets up an analysis of a discord message.

    Returns
    -------
    models.Message
        A Redis model of a Discord message
    """
    content = "The quick brown fox jumps over the lazy dog."
    embedding = await vectorizer.aencode(content)
    return models.MessageAnalysis(
        message_id="1",
        channel_id="1",
        guild_id="1",
        timestamp=datetime.datetime.fromtimestamp(0, datetime.UTC),
        embedding=embedding,
        user_id="1",
        sentiment=calculate_sentiment(content),
    )


@pytest_asyncio.fixture(scope="session")
async def vectorized_message(
    message: models.MessageAnalysis,
) -> models.VectorizedMessage:
    """Fixture that creates a models.VectorizedMessage.

    Returns
    -------
    models.VectorizedMessage
        A message with embedding vector
    """
    # NOTE: This works because BaseModel ignores extra fields
    return models.VectorizedMessage(**message.model_dump())


async def test__save_message(
    redis: Redis,
    message: models.MessageAnalysis,
) -> None:
    """
    Tests whether the save_mesage function stores the message on Redis.

    Asserts
    -------
    - The returned key is the same as the one constructed by the key_schema
    """
    key = await save_message(redis, message)
    assert key == key_schema.guild_messages(
        guild_id=message.guild_id,
        message_id=message.message_id,
    )


async def test__get_similar_message(
    redis: Redis,
    message: models.MessageAnalysis,
    vectorized_message: models.VectorizedMessage,
) -> None:
    """
    Tests that the same message is returned by the get_similar_messages function.

    Asserts
    -------
    - The returned message is the same message whose embedding vector was used
    """
    await save_message(redis, message)
    messages = await get_similar_messages(redis, vectorized_message)
    assert len(messages) == 1
    redis_message = messages[0]
    assert redis_message.channel_id == message.channel_id
    assert redis_message.guild_id == message.guild_id
    assert redis_message.message_id == message.message_id
    assert message.timestamp == message.timestamp
