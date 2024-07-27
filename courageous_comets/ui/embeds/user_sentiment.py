import discord

from courageous_comets.ui.components import user_sentiment
from courageous_comets.ui.embeds import format_embed


def render(user: str, compound: float) -> discord.Embed:
    """
    Render the sentiment analysis results for the given user into an embed.

    Parameters
    ----------
    user : str
        The user's name.
    compound : float
        The compound sentiment score.

    Returns
    -------
    discord.Embed
        The rendered embed.
    """
    embed = discord.Embed(
        title="User Sentiment",
        description=user_sentiment.render(user, compound),
        timestamp=discord.utils.utcnow(),
    )
    return format_embed(embed)
