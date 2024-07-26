import datetime

import pytest
import pytest_asyncio
from redis.asyncio import Redis

from courageous_comets import models
from courageous_comets.redis.keys import key_schema
from courageous_comets.redis.messages import (
    get_messages_by_semantics_similarity,
    get_messages_by_sentiment_similarity,
    get_recent_messages,
    save_message,
)
from courageous_comets.sentiment import calculate_sentiment
from courageous_comets.vectorizer import Vectorizer
from courageous_comets.words import tokenize_sentence, word_frequency


@pytest.fixture(scope="session")
def content() -> str:
    """Fixture that sets up the content of message.

    Returns
    -------
    str
        The message content.
    """
    return "The quick brown fox jumps over the lazy dog."


@pytest.fixture(scope="session")
def sentiment(content: str) -> models.SentimentResult:
    """Fixture that calculates the sentiment analysis of content.

    Parameters
    ----------
    content: str
        The text to run the sentiment analysis on.

    Returns
    -------
    models.SentimentResult
        The result of the sentiment analysis.
    """
    return calculate_sentiment(content)


@pytest_asyncio.fixture(scope="session")
async def message(
    content: str,
    vectorizer: Vectorizer,
    sentiment: models.SentimentResult,
) -> models.MessageAnalysis:
    """Fixture that creates a message to be stored on Redis.

    Parameters
    ----------
    content: str
        The contents of the message.
    vectorizer: courageous_comets.vectorizer.Vectorizer
        The model that creates the embedding vector of content.
    sentiment: models.SentimentResult
        The result of the sentiment analysis of content.

    Returns
    -------
    courageous_comets.models.MessageAnalysis
        An analysis of the message contents.
    """
    embedding = await vectorizer.aencode(content)
    tokens = tokenize_sentence(content)
    return models.MessageAnalysis(
        message_id="1",
        channel_id="1",
        guild_id="1",
        timestamp=datetime.datetime.fromtimestamp(0, datetime.UTC),
        user_id="1",
        embedding=embedding,
        sentiment=sentiment,
        tokens=word_frequency(tokens),
    )


async def test__save_message(
    redis: Redis,
    message: models.MessageAnalysis,
) -> None:
    """
    Tests whether the save_mesage function stores the message on Redis.

    Parameters
    ----------
    redis: redis.Redis
        The Redis connection instance.
    message: courageous_comets.models.MessageAnalysis
        The Discord message with an embedding vector of its content.

    Asserts
    -------
    - The returned key is the same as the one constructed by the key_schema
    """
    key = await save_message(redis, message)
    assert key == key_schema.guild_messages(
        guild_id=int(message.guild_id),
        message_id=int(message.message_id),
    )


async def test__get_messages_by_semantics_similarity(
    redis: Redis,
    message: models.MessageAnalysis,
) -> None:
    """
    Tests that the same message is returned from a semantics similarity search.

    Parameters
    ----------
    redis: redis.Redis
        The Redis connection instance.
    message: courageous_comets.models.MessageAnalysis
        The message to save.

    Asserts
    -------
    - The same message is returned using a semantics similarity search.
    """
    await save_message(redis, message)
    messages = await get_messages_by_semantics_similarity(
        redis,
        guild_id=message.guild_id,
        embedding=message.embedding,
    )
    assert len(messages) == 1
    assert messages[0].message_id == message.message_id


async def test__get_messages_by_sentiment_similarity(
    redis: Redis,
    message: models.MessageAnalysis,
    sentiment: models.SentimentResult,
) -> None:
    """
    Tests that the same message is returned from a sentiment similarity search.

    Parameters
    ----------
    redis: redis.Redis
        The Redis connection instance.
    message: courageous_comets.models.MessageAnalysis
        The message to save.
    sentiment : courageous_comets.models.SentimentResult
        The sentiment analayis result of message.

    Asserts
    -------
    - The same message is returned using a sentiment similarity search.
    """
    await save_message(redis, message)
    messages = await get_messages_by_sentiment_similarity(
        redis,
        guild_id=message.guild_id,
        sentiment=sentiment.compound,
        radius=0.1,
    )
    assert len(messages) == 1
    assert messages[0].message_id == message.message_id


@pytest.mark.parametrize(("limit", "expect"), [(10, 10), (150, 100)])
@pytest.mark.num_messages(100)
async def test__get_recent_messages(
    redis: Redis,
    messages: list[models.MessageAnalysis],
    limit: int,
    expect: int,
) -> None:
    """Tests that the expected number of messages are returned from Redis.

    Parameters
    ----------
    redis: redis.Redis
        The Redis connection instance.
    messages list[courageous_comets.models.MessageAnalysis]
        The messages to save

    Asserts
    -------
    - The number of mesages returned does not exceed specified limit.
    """
    # Save the messages to the database.
    for message in messages:
        await save_message(redis, message)
    # All messages have the same guild_id
    guild_id = messages[0].guild_id

    # Update its timestamp with the provided message_timestamp
    db_messages = await get_recent_messages(redis, guild_id=guild_id, limit=limit)
    assert len(db_messages) == expect
