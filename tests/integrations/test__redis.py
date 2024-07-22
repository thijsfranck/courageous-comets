import datetime

import pytest
import pytest_asyncio
from redis.asyncio import Redis

from courageous_comets import models
from courageous_comets.redis.keys import key_schema
from courageous_comets.redis.messages import get_similar_messages, save_message
from courageous_comets.vectorizer import Vectorizer


@pytest.fixture(scope="session")
def message() -> models.Message:
    """Fixture that sets up a message.

    Returns
    -------
    models.Message
        A Redis model of a Discord message
    """
    return models.Message(
        message_id="1",
        channel_id="1",
        guild_id="1",
        timestamp=datetime.datetime.fromtimestamp(0, datetime.UTC),
        user_id="1",
        content="The quick brown fox jumps over the lazy dog.",
    )


@pytest_asyncio.fixture(scope="session")
async def vectorized_message(
    message: models.Message,
    vectorizer: Vectorizer,
) -> models.VectorizedMessage:
    """Fixture that creates an embedding vector of contents of message.

    Returns
    -------
    models.VectorizedMessage
        A message with embedding vector
    """
    embedding = await vectorizer.embed(message.content)
    return models.VectorizedMessage(**message.model_dump(), embedding=embedding)


async def test__save_message(
    redis: Redis,
    vectorized_message: models.VectorizedMessage,
) -> None:
    """
    Tests whether the save_mesage function stores the message on Redis.

    Asserts
    -------
    - The returned key is the same as the one constructed by the key_schema
    """
    key = await save_message(redis, vectorized_message)
    assert key == key_schema.guild_messages(
        guild_id=vectorized_message.guild_id,
        message_id=vectorized_message.message_id,
    )


async def test__get_similar_message(
    redis: Redis,
    message: models.Message,
    vectorized_message: models.VectorizedMessage,
) -> None:
    """
    Tests that the same message is returned by the get_similar_messages function.

    Asserts
    -------
    - The returned message is the same message whose embedding vector was used
    """
    await save_message(redis, vectorized_message)
    messages = await get_similar_messages(redis, message, vectorized_message.embedding)
    assert len(messages) == 1
    assert messages[0].model_dump() == message.model_dump()
