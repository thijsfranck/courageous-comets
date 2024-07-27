import discord

from courageous_comets import __version__
from courageous_comets.ui.embeds import format_embed

TEMPLATE = """
{body}

Click the link in the header to visit the documentation!
"""


def render(body: str) -> discord.Embed:
    """
    Render the about message into an embed.

    Parameters
    ----------
    body : str
        The body of the about message.

    Returns
    -------
    discord.Embed
        The rendered embed.
    """
    embed = discord.Embed(
        title="About Courageous Comets",
        description=TEMPLATE.format_map({"body": body}),
        color=discord.Color.blurple(),
        url=f"https://thijsfranck.github.io/courageous-comets/{__version__}/",
        timestamp=discord.utils.utcnow(),
    )
    return format_embed(embed)
