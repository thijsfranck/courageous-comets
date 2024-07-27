from courageous_comets.ui.components import sentiment

TEMPLATE = """
Overall the sentiment of {user} is **{sentiment}**.
Their average compound score is {compound}.
"""


def render(user: str, compound: float) -> str:
    """
    Render the sentiment analysis score for the given user into a string.

    Parameters
    ----------
    user : str
        The user's name.
    compound : float
        The compound sentiment score.

    Returns
    -------
    str
        The rendered sentiment analysis results.
    """
    return TEMPLATE.format_map(
        {
            "user": user,
            "compound": compound,
            "sentiment": sentiment.render(compound),
        },
    )
