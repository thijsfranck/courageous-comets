from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture, MockType
from redis.asyncio import Redis

from .sentiment import (
    MAX_MESSAGE_LENGTH,
    calculate_sentiment,
    get_sentiment,
    logger,
    store_sentiment,
)


@pytest.fixture()
def redis(mocker: MockerFixture) -> MockerFixture:
    """Create a mock Redis instance for testing."""
    mock = mocker.AsyncMock(spec=Redis)
    mock.hset = mocker.AsyncMock()
    mock.hmget = mocker.AsyncMock()
    return mock


def test__calculate_sentiment_analyzes_sentiment_of_given_text() -> None:
    """
    Test whether the sentiment calculation analyzes the sentiment of the given text.

    Asserts
    -------
    - The function produces sentiment scores for the given text.
    """
    result = calculate_sentiment("I love this product!", "test")
    attrs = ["neg", "neu", "pos", "compound"]
    for attr in attrs:
        assert getattr(result, attr) is not None


@pytest.mark.parametrize(
    ("message", "expected"),
    [
        ("a" * MAX_MESSAGE_LENGTH, False),
        ("a" * (MAX_MESSAGE_LENGTH + 1), True),
    ],
)
def test__calculate_sentiment_truncates_long_messages(
    *,
    mocker: MockerFixture,
    message: str,
    expected: bool,
) -> None:
    """
    Test whether the sentiment calculation truncates long messages.

    Asserts
    -------
    - The function truncates messages longer than 256 characters.
    """
    logger_warning = mocker.spy(logger, "warning")
    calculate_sentiment(message, "test")
    assert logger_warning.called == expected


@pytest.mark.asyncio()
async def test__store_sentiment_calculates_and_stores_sentiment(
    *,
    mocker: MockerFixture,
    redis: MockType,
) -> None:
    """
    Test whether the store sentiment function calculates and stores the sentiment of a message.

    Asserts
    -------
    - The sentiment is calculated for the message content.
    - The sentiment is stored in the database.
    """
    message = mocker.Mock(
        content="I love this product!",
        guild=Mock(id=1),
        channel=Mock(id=1),
        author=Mock(id=1),
        id=1,
    )

    await store_sentiment(message, redis)

    redis.hset.assert_awaited_with(
        "courageous_comets:1:1:1:1:sentiment",
        mapping={
            "neg": mocker.ANY,
            "neu": mocker.ANY,
            "pos": mocker.ANY,
            "compound": mocker.ANY,
        },
    )


@pytest.mark.asyncio()
async def test__store_sentiment_ignores_empty_messages(
    *,
    mocker: MockerFixture,
    redis: MockType,
) -> None:
    """
    Test whether the store sentiment function ignores empty messages.

    Asserts
    -------
    - The database is not updated when the message is empty.
    """
    message = mocker.Mock(content="")
    await store_sentiment(message, redis)
    redis.hset.assert_not_awaited()


@pytest.mark.parametrize(
    "message",
    [
        Mock(content="test", guild=None, channel=None, author=None, id=1),
        Mock(content="test", guild=Mock(id=1), channel=None, author=None, id=1),
        Mock(content="test", guild=Mock(id=1), channel=Mock(id=1), author=None, id=1),
    ],
)
@pytest.mark.asyncio()
async def test__store_sentiment_ignores_messages_without_ids(
    *,
    redis: MockType,
    message: MockType,
) -> None:
    """
    Test whether the store sentiment function ignores messages without IDs.

    Asserts
    -------
    - The database is not updated when the message is missing IDs.
    """
    await store_sentiment(message, redis)
    redis.hset.assert_not_awaited()


@pytest.mark.asyncio()
async def test__get_sentiment_retrieves_sentiment_from_redis(
    *,
    redis: MockType,
) -> None:
    """
    Test whether the get sentiment function retrieves the sentiment of a message from Redis.

    Asserts
    -------
    - The sentiment is retrieved from the database.
    """
    key = "courageous_comets:1:1:1:1:sentiment"
    redis.hmget.return_value = ["1.0", "1.0", "1.0", "1.0"]

    result = await get_sentiment(key, redis)

    redis.hmget.assert_awaited_with(key, "neg", "neu", "pos", "compound")
    assert result.model_dump(mode="json") == {
        "neg": 1.0,
        "neu": 1.0,
        "pos": 1.0,
        "compound": 1.0,
    }


@pytest.mark.asyncio()
async def test__get_sentiment_handles_missing_sentiment(
    *,
    redis: MockType,
) -> None:
    """
    Test whether the get sentiment function handles missing sentiment in Redis.

    Asserts
    -------
    - The function returns default sentiment values when the sentiment is missing.
    """
    key = "courageous_comets:1:1:1:1:sentiment"
    redis.hmget.return_value = [None, None, None, None]

    result = await get_sentiment(key, redis)

    redis.hmget.assert_awaited_with(key, "neg", "neu", "pos", "compound")
    assert result.model_dump(mode="json") == {
        "neg": 0.0,
        "neu": 0.0,
        "pos": 0.0,
        "compound": 0.0,
    }
