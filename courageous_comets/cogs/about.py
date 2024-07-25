import logging

import discord
from discord import Embed, app_commands
from discord.ext import commands

from courageous_comets import __version__

logger = logging.getLogger(__name__)


DESCRIPTION = """
Thank you for using Courageous Comets! ☄️

This is a Discord app that provides various statistical analyses on messages.

- **Sentiment Analysis**: Analyze the sentiment of a message.
- **Word Frequency**: Analyze the frequency of words in a message.
- **Similarity Analysis**: Analyze the similarity between two messages.

Click the link in the header to visit the documentation!
"""


def render() -> Embed:
    """Render the about message."""
    return Embed(
        title=f"Courageous Comets ({__version__})",
        description=DESCRIPTION,
        color=discord.Color.blurple(),
        url=f"https://thijsfranck.github.io/courageous-comets/{__version__}/",
        timestamp=discord.utils.utcnow(),
    )


class About(commands.Cog):
    """A cog that provides information about the app upon request."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(
        name="about",
        description="Get information about the app.",
    )
    async def about(self, interaction: discord.Interaction) -> None:
        """
        Respond to the `/about` command with information about the app.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction that triggered the command
        """
        logger.info(
            "User %s requested the about message using the /about command.",
            interaction.user.id,
        )
        try:
            await interaction.response.send_message(embed=render(), ephemeral=True)
        except discord.HTTPException as e:
            logger.exception("Could not deliver the about message.", exc_info=e)


async def setup(bot: commands.Bot) -> None:
    """Load the cog."""
    await bot.add_cog(About(bot))
