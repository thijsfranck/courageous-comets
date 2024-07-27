import discord

from courageous_comets.models import SentimentResult
from courageous_comets.ui.components import sentiment
from courageous_comets.ui.embeds import format_embed

TEMPLATE = """
Overall the sentiment of the message is **{sentiment}**.
"""


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

    template_vars = {
        "sentiment": sentiment.render(data.compound),
    }

    embed = discord.Embed(
        title="Message Sentiment",
        description=TEMPLATE.format_map(template_vars),
        color=color,
        timestamp=discord.utils.utcnow(),
    )

    embed.add_field(
        name="Negative",
        value=f"{int(data.neg * 100)}%",
        inline=True,
    )

    embed.add_field(
        name="Neutral",
        value=f"{int(data.neu * 100)}%",
        inline=True,
    )

    embed.add_field(
        name="Positive",
        value=f"{int(data.pos * 100)}%",
        inline=True,
    )

    return format_embed(embed)
