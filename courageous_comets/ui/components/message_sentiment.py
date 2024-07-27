from courageous_comets.models import SentimentResult
from courageous_comets.ui.components import sentiment

TEMPLATE = """
Overall the sentiment of the message is **{sentiment}**.

Here's a breakdown of the scores:

- Negative: {neg}
- Neutral: {neu}
- Positive: {pos}

The compound score is {compound}.
"""


def render(data: SentimentResult) -> str:
    """
    Render the sentiment analysis results into a string.

    Returns
    -------
    str
        The rendered sentiment analysis results.
    """
    return TEMPLATE.format_map(
        {
            **data.model_dump(),
            "sentiment": sentiment.render(data.compound),
        },
    )
