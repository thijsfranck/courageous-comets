import logging

import discord
from discord import Embed, app_commands
from discord.ext import commands

from courageous_comets import __version__

logger = logging.getLogger(__name__)


class About(commands.Cog):
    """A cog that provides information about the app upon request."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(
        name="about",
        description="Get information about the app.",
    )
    async def about_command(self, interaction: discord.Interaction) -> None:
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
            await interaction.response.send_message(
                embed=Embed(
                    title=f"Courageous Comets ({__version__})",
                    description=self.bot.description,
                    color=discord.Color.blurple(),
                    url=f"https://thijsfranck.github.io/courageous-comets/{__version__}/",
                    timestamp=discord.utils.utcnow(),
                ),
                ephemeral=True,
            )
        except discord.HTTPException as e:
            logger.exception("Could not deliver the about message.", exc_info=e)


async def setup(bot: commands.Bot) -> None:
    """Load the cog."""
    await bot.add_cog(About(bot))