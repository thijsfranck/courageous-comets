import discord

from courageous_comets.ui.components import search_results
from courageous_comets.ui.embeds import format_embed


def render(query: str, messages: list[discord.Message]) -> discord.Embed:
    """
    Render a list of messages into an embed.

    Parameters
    ----------
    query : str
        The query used to find the messages.
    messages : list[discord.Message]
        The messages to render.

    Returns
    -------
    discord.Embed
        The rendered embed.
    """
    embed = discord.Embed(
        title="Search Results 🚀",
        description=search_results.render(query, messages),
        colour=discord.Colour.blurple(),
        timestamp=discord.utils.utcnow(),
    )
    return format_embed(embed)
