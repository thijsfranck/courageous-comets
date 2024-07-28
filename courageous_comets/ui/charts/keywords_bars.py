import io
from collections import Counter

import discord
import matplotlib.pyplot as plt


def render(counter: Counter[str]) -> discord.File:
    """
    Render a bar chart of the top given keywords.

    Parameters
    ----------
    counter: Counter[str]
        The keywords and their counts.
    """
    keywords, counts = zip(*counter.most_common(10), strict=True)

    _, ax = plt.subplots()
    ax.bar(keywords, counts)
    ax.set_ylabel("Count")
    ax.set_title("Top keywords")

    # Rotate the x-axis labels 45 degrees to keep them readable
    plt.xticks(rotation=45, ha="right")

    file_ = io.BytesIO()
    plt.savefig(file_)
    file_.seek(0)

    return discord.File(file_, "top_keywords.png")
