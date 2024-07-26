import logging

from nltk.sentiment import SentimentIntensityAnalyzer

from courageous_comets.models import SentimentResult

logger = logging.getLogger(__name__)


def calculate_sentiment(content: str) -> SentimentResult:
    """
    Calculate the sentiment of a message.

    Uses the NLTK sentiment intensity analyzer.

    Parameters
    ----------
    content : str
        The message content to analyze.

    Returns
    -------
    courageous_comets.models.SentimentResult
        The sentiment of the message.
    """
    sia = SentimentIntensityAnalyzer()
    result = sia.polarity_scores(content)

    return SentimentResult.model_validate(result)
