from pathlib import Path

import matplotlib.pyplot as plt

from courageous_comets import models


def plot_sentiment_analysis(
    message_id: str | int,
    analysis_result: models.SentimentResult,
) -> Path:
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
    Path
        The path to the saved image.
    """
    chart_dir = Path("artifacts/charts/sentiment").resolve()
    chart_dir.mkdir(parents=True, exist_ok=True)
    chart_path = chart_dir / f"{message_id}.png"

    if chart_path.exists():
        return chart_path

    _, ax = plt.subplots()
    ax.bar(
        [
            "Negative",
            "Neutral",
            "Positive",
        ],
        [
            analysis_result.neg,
            analysis_result.neu,
            analysis_result.pos,
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

    return chart_path
