import discord

from courageous_comets import __version__


def format_embed(embed: discord.Embed) -> discord.Embed:
    """
    Format the given embed for consistent branding across interactions.

    Includes a footer with the version of the app.

    Parameters
    ----------
    embed : discord.Embed
        The embed to format.

    Returns
    -------
    discord.Embed
        The formatted embed.
    """
    footer_text = f"Generated using Courageous Comets {__version__}"
    embed.set_footer(text=footer_text)
    return embed
