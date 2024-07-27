SENTIMENT: dict[range, str] = {
    range(-100, -50): "very negative 😡",
    range(-50, -10): "negative 🙁",
    range(-10, 10): "neutral 🙂",
    range(10, 50): "positive 😁",
    range(50, 100): "very positive 😍",
}


def render(compound: float) -> str:
    """
    Render the given sentiment score into a string.

    Parameters
    ----------
    compound : float
        The compound sentiment score.

    Returns
    -------
    str
        The rendered sentiment.
    """
    for score_range, sentiment in SENTIMENT.items():
        if int(compound * 100) in score_range:
            return sentiment

    return "unknown 😶"
