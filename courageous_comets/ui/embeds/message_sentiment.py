import discord

from courageous_comets.models import SentimentResult
from courageous_comets.ui.components import message_sentiment
from courageous_comets.ui.embeds import format_embed


def render(data: SentimentResult) -> discord.Embed:
    """
    Render the sentiment analysis results into an embed.

    Parameters
    ----------
    data : SentimentResult
        The sentiment analysis results.

    Returns
    -------
    discord.Embed
        The rendered embed.
    """
    color = discord.Color.green() if data.compound >= 0 else discord.Color.red()

    embed = discord.Embed(
        title="Message Sentiment",
        description=message_sentiment.render(data),
        color=color,
        timestamp=discord.utils.utcnow(),
    )

    return format_embed(embed)
