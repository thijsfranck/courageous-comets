from collections.abc import AsyncGenerator
from typing import cast

import pytest
import pytest_asyncio
from faker import Faker
from redis.asyncio import Redis

from courageous_comets import models, settings
from courageous_comets.client import CourageousCometsBot
from courageous_comets.sentiment import calculate_sentiment
from courageous_comets.vectorizer import Vectorizer
from courageous_comets.words import tokenize_sentence, word_frequency


@pytest.fixture()
async def bot() -> AsyncGenerator[CourageousCometsBot, None]:
    """Fixture that sets up and tears down the CourageousCometsBot instance."""
    instance = CourageousCometsBot()
    await instance.setup_hook()
    yield instance
    await instance.close()


@pytest.fixture()
async def redis(bot: CourageousCometsBot) -> AsyncGenerator[Redis, None]:
    """Acquire a connection to the Redis database with teardown."""
    instance = cast(Redis, bot.redis)

    yield instance

    # Delete any keys that were created during the test
    keys_to_delete = [key async for key in instance.scan_iter(f"{settings.REDIS_KEYS_PREFIX}:*")]

    if keys_to_delete:
        await instance.delete(*keys_to_delete)

    await instance.aclose()


@pytest_asyncio.fixture
async def messages(
    vectorizer: Vectorizer,
    faker: Faker,
    request: pytest.FixtureRequest,
) -> list[models.MessageAnalysis]:
    """Generate messages using the num_messages mark."""
    mark = request.node.get_closest_marker("num_messages")
    num_messages = int(mark.args[0]) if mark and len(mark.args) > 0 else 10
    messages: list[models.MessageAnalysis] = []
    min_id = 1
    max_id = 1_0000_000
    for _ in range(num_messages):
        sentence = faker.sentence(nb_words=10)
        embedding = await vectorizer.aencode(sentence)
        sentiment = calculate_sentiment(sentence)
        tokens = tokenize_sentence(sentence)
        messages.append(
            models.MessageAnalysis(
                guild_id="1",
                channel_id=str(faker.random_int(min=min_id, max=5)),  # 5 channels
                message_id=str(faker.random_int(min=min_id, max=max_id)),
                user_id=str(faker.random_int(min=min_id, max=5)),  # 5 users
                timestamp=faker.date_time(),
                embedding=embedding,
                sentiment=sentiment,
                tokens=word_frequency(tokens),
            ),
        )
    return messages
