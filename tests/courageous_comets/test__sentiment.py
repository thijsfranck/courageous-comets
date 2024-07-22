import pytest
from pytest_mock import MockerFixture
from redis.asyncio import Redis

from courageous_comets.models import SentimentResult
from courageous_comets.sentiment import (
    MAX_MESSAGE_LENGTH,
    calculate_sentiment,
    logger,
)


@pytest.fixture()
def redis(mocker: MockerFixture) -> MockerFixture:
    """Create a mock Redis instance for testing."""
    mock = mocker.AsyncMock(spec=Redis)
    mock.hset = mocker.AsyncMock()
    mock.hmget = mocker.AsyncMock()
    return mock


def test__calculate_sentiment_analyzes_sentiment_of_given_text(
    mocker: MockerFixture,
) -> None:
    """
    Test whether the sentiment calculation analyzes the sentiment of the given text.

    Asserts
    -------
    - The function produces sentiment scores for the given text.
    """
    expected = SentimentResult.model_construct(
        neg=mocker.ANY,
        neu=mocker.ANY,
        pos=mocker.ANY,
        compound=mocker.ANY,
    )
    result = calculate_sentiment("I love this product!")
    assert result == expected


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
    calculate_sentiment(message)
    assert logger_warning.called == expected
