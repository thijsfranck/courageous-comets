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
    keywords = [keyword for keyword, _ in counter.most_common(10)]
    counts = [count for _, count in counter.most_common(10)]

    _, ax = plt.subplots()
    ax.bar(keywords, counts)
    ax.set_ylabel("Count")
    ax.set_title("Top keywords")

    file_ = io.BytesIO()
    plt.savefig(file_)
    file_.seek(0)

    return discord.File(file_, "top_keywords.png")
