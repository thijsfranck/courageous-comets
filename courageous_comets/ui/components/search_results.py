import discord

from courageous_comets.ui.components import message_list

TEMPLATE = """
The most recent messages related to your query are:

{results}

You searched for: `{query}`
"""


def render(query: str, messages: list[discord.Message]) -> str:
    """
    Render a list of messages into search results.

    Parameters
    ----------
    query : str
        The query used to find the messages.
    messages : list[discord.Message]
        The messages to render.

    Returns
    -------
    str
        The rendered search results
    """
    return TEMPLATE.format_map(
        {
            "results": message_list.render(messages),
            "query": query,
        },
    )
