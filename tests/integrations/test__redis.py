import datetime

import pytest
import pytest_asyncio
from redis.asyncio import Redis

from courageous_comets import models
from courageous_comets.redis.keys import key_schema
from courageous_comets.redis.messages import (
    get_messages_by_semantics_similarity,
    get_messages_by_sentiment_similarity,
    get_previous_messages,
    save_message,
)
from courageous_comets.sentiment import calculate_sentiment
from courageous_comets.vectorizer import Vectorizer


@pytest.fixture(scope="session")
def message() -> models.Message:
    """Fixture that sets up a message.

    Returns
    -------
    courageous_comets.models.Message
        A Redis model of a Discord message
    """
    return models.Message(
        message_id="1",
        channel_id="1",
        guild_id="1",
        timestamp=datetime.datetime.fromtimestamp(0, datetime.UTC),
        user_id="1",
    )


@pytest.fixture(scope="session")
def content() -> str:
    """Fixture that sets up the content of message.

    Returns
    -------
    str
        The message content.
    """
    return "The quick brown fox jumps over the lazy dog."


@pytest_asyncio.fixture(scope="session")
async def vectorized_message(
    message: models.Message,
    content: str,
    vectorizer: Vectorizer,
) -> models.VectorizedMessage:
    """Fixture that creates an embedding vector of contents of message.

    Parameters
    ----------
    message: courageous_comets.models.Message
        The (base) model of the Discord message.
    content:
        The contents of the message.
    vectorizer: courageous_comets.vectorizer.Vectorizer
        The model that creates the embedding vector of content

    Returns
    -------
    courageous_comets.models.VectorizedMessage
        A message with embedding vector of contents.
    """
    embedding = await vectorizer.aencode(content)
    return models.VectorizedMessage(**message.model_dump(), embedding=embedding)


@pytest.fixture(scope="session")
def sentiment(content: str) -> models.SentimentResult:
    """Fixture that calculates the sentiment analysis of content.

    Parameters
    ----------
    content:
        The text to run the sentiment analysis on.

    Returns
    -------
    models.SentimentResult
        The result of the sentiment analysis.
    """
    return calculate_sentiment(content)


async def test__save_message(
    redis: Redis,
    vectorized_message: models.VectorizedMessage,
    sentiment: models.SentimentResult,
) -> None:
    """
    Tests whether the save_mesage function stores the message on Redis.

    Parameters
    ----------
    redis: redis.Redis
        The Redis connection instance.
    vectorized_message: courageous_comets.models.VectorizedMessage
        The Discord message with an embedding vector of its content.
    sentiment : courageous_comets.models.SentimentResult
        The sentiment analayis result of a message.

    Asserts
    -------
    - The returned key is the same as the one constructed by the key_schema
    """
    key = await save_message(redis, vectorized_message, sentiment)
    assert key == key_schema.guild_messages(
        guild_id=int(vectorized_message.guild_id),
        message_id=int(vectorized_message.message_id),
    )


async def test__get_messages_by_semantics_similarity(
    redis: Redis,
    message: models.Message,
    vectorized_message: models.VectorizedMessage,
    sentiment: models.SentimentResult,
) -> None:
    """
    Tests that the same message is returned by the get_similar_messages function.

    Parameters
    ----------
    redis: redis.Redis
        The Redis connection instance.
    message: courageous_comets.models.Message
        The (base) model of the Discord message.
    vectorized_message: courageous_comets.models.VectorizedMessage
        The Discord message with an embedding vector of its content.
    sentiment : courageous_comets.models.SentimentResult
        The sentiment analayis result of a message.

    Asserts
    -------
    - The returned message is the same message whose embedding vector was used
    """
    await save_message(redis, vectorized_message, sentiment)
    messages = await get_messages_by_semantics_similarity(
        redis,
        message,
        vectorized_message.embedding,
    )
    assert len(messages) == 1
    assert messages[0].model_dump() == message.model_dump()


async def test__get_messages_by_sentiment_similarity(
    redis: Redis,
    message: models.Message,
    vectorized_message: models.VectorizedMessage,
    sentiment: models.SentimentResult,
) -> None:
    """
    Tests that the same message is returned by the get_messages_by_sentiment_similarity function.

    Parameters
    ----------
    redis: redis.Redis
        The Redis connection instance.
    message: courageous_comets.models.Message
        The (base) model of the Discord message.
    vectorized_message: courageous_comets.models.VectorizedMessage
        The Discord message with an embedding vector of its content.
    sentiment : courageous_comets.models.SentimentResult
        The sentiment analayis result of a message.

    Asserts
    -------
    - The returned message is the same message whose sentiment analysis result was used
    """
    await save_message(redis, vectorized_message, sentiment)
    messages = await get_messages_by_sentiment_similarity(
        redis,
        message,
        sentiment,
        radius=0.1,
    )
    assert len(messages) == 1
    assert messages[0].model_dump() == message.model_dump()


@pytest.mark.parametrize(
    ("message_timestamp", "expected_output"),
    [(datetime.datetime.fromtimestamp(0, datetime.UTC), 1)],
)
async def test__get_previous_messages(  # noqa: PLR0913
    redis: Redis,
    message: models.Message,
    vectorized_message: models.VectorizedMessage,
    sentiment: models.SentimentResult,
    message_timestamp: datetime.datetime,
    expected_output: int,
) -> None:
    """
    Tests that the correct number of messages are returned from `get_previous_messages`.

    Parameters
    ----------
    redis: redis.Redis
        The Redis connection instance.
    message: courageous_comets.models.Message
        The (base) model of the Discord message.
    vectorized_message: courageous_comets.models.VectorizedMessage
        The Discord message with an embedding vector of its content.
    sentiment: courageous_comets.models.SentimentResult
        The sentiment analayis result of the message
    message_timestamp: datetime.datetime
        The timestamp of the comparison message.
    expected_output: int
        The number of messages with timestamp older than or equal to `message_timestamp`

    Asserts
    -------
    - The number of messages returned is equal to the expected_output.
    """
    # Save the default message to the database.
    await save_message(redis, vectorized_message, sentiment)
    # Update its timestamp with the provided message_timestamp
    message.timestamp = message_timestamp
    messages = await get_previous_messages(redis, message)
    assert len(messages) == expected_output
