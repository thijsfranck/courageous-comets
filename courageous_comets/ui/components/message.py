import discord

TEMPLATE = """
{author} {timestamp}:
{content}
"""


def _shorten(string: str, *, limit: int = 50) -> str:
    """Trim a string if necessary given `limit`."""
    if len(string) > limit:
        string = string[: limit - 3] + "..."
    return string


def render(message: discord.Message) -> str:
    """
    Format a message into a string.

    Parameters
    ----------
    message : discord.Message
        The message to format.

    Returns
    -------
    str
        The formatted string.
    """
    return TEMPLATE.format_map(
        {
            "author": message.author.mention,
            "timestamp": discord.utils.format_dt(message.created_at, style="R"),
            "content": _shorten(message.clean_content),
        },
    )
