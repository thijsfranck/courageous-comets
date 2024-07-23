import logging

from nltk.sentiment import SentimentIntensityAnalyzer

from courageous_comets.models import SentimentResult

MAX_MESSAGE_LENGTH = 256

logger = logging.getLogger(__name__)


def calculate_sentiment(content: str) -> SentimentResult:
    """
    Calculate the sentiment of a message.

    Uses the NLTK sentiment intensity analyzer to calculate the sentiment of a message.

    Messages can be up to 256 characters long. If a message is longer than 256 characters,
    it will be truncated.

    Parameters
    ----------
    content : str
        The message content to analyze.

    Returns
    -------
    courageous_comets.models.SentimentResult
        The sentiment of the message.
    """
    truncated = content[:MAX_MESSAGE_LENGTH]

    if truncated != content:
        logger.warning("Truncated message to %s characters", MAX_MESSAGE_LENGTH)

    sia = SentimentIntensityAnalyzer()
    result = sia.polarity_scores(truncated)

    return SentimentResult.model_validate(result)
