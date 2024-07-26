import pytest
from pytest_mock import MockerFixture
from redis.asyncio import Redis

from courageous_comets.models import SentimentResult
from courageous_comets.sentiment import (
    calculate_sentiment,
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
