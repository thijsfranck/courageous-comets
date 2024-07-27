import discord

from courageous_comets.ui.components import message


def render(messages: list[discord.Message]) -> str:
    """
    Format a list of messages into a string.

    Parameters
    ----------
    messages : list[discord.Message]
        The messages to format.

    Returns
    -------
    str
        The formatted string.
    """
    return "".join(map(message.render, messages))
