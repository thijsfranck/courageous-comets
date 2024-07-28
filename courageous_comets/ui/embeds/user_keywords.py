from collections import Counter

import discord

from courageous_comets.ui.embeds import format_embed


def render(user: discord.User | discord.Member, keywords: Counter[str]) -> discord.Embed:
    """
    Render the top keywords used by a user.

    Parameters
    ----------
    user: discord.User | discord.Member
        The user to show the keywords for.
    keywords: Counter[str]
        The keywords and their counts.
    """
    embed = discord.Embed(
        title="User Interests",
        description=f"Here are the top keywords that {user.mention} has used in their messages.",
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
