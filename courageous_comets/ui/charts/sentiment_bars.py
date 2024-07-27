import discord
import matplotlib.pyplot as plt

from courageous_comets import models
from courageous_comets.ui.charts import CACHE_ROOT

CACHE_DIR = CACHE_ROOT / "sentiment_bars"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def render(
    message_id: str | int,
    data: models.SentimentResult,
) -> discord.File:
    """
    Plot the sentiment analysis of a message.

    Creates a bar chart of the sentiment analysis of a message and saves it to a file.
    If the file already exists, it will be returned instead of being recreated.

    Parameters
    ----------
    message_id : str | int
        The id of the message.
    analysis_result : SentimentResult
        The result of sentiment analysis on a message.

    Returns
    -------
    discord.File
        The file containing the saved image.

    Notes
    -----
    Charts are cached in the `CACHE_DIR` directory using the message id as the filename.
    """
    chart_path = CACHE_DIR / f"{message_id}.png"

    if chart_path.exists():
        return discord.File(chart_path, filename=f"{message_id}.png")

    _, ax = plt.subplots()
    ax.bar(
        [
            "Negative",
            "Neutral",
            "Positive",
        ],
        [
            data.neg,
            data.neu,
            data.pos,
        ],
        color=[
            "red",
            "blue",
            "green",
        ],
    )
    ax.set_ylabel("Sentiment Score")
    ax.set_title("Sentiment Analysis")

    plt.savefig(chart_path)

    return discord.File(chart_path, filename=f"{message_id}.png")
