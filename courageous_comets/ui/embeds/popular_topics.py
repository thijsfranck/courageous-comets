from collections import Counter

import discord

from courageous_comets.enums import StatisticScope
from courageous_comets.ui.embeds import format_embed


def render(scope: StatisticScope, keywords: Counter[str]) -> discord.Embed:
    """
    Render the top keywords used in the given scope.

    Parameters
    ----------
    user: StatisticsScope
        The scope to show the keywords for.
    keywords: Counter[str]
        The keywords and their counts.
    """
    embed = discord.Embed(
        title="Popular Topics",
        description=f"Here are the top keywords for the current **{scope.name.lower()}**.",
        color=discord.Color.blurple(),
        timestamp=discord.utils.utcnow(),
    )

    for keyword, count in keywords.most_common(3):
        embed.add_field(
            name=keyword,
            value=f"{count} times",
            inline=True,
        )

    return format_embed(embed)
