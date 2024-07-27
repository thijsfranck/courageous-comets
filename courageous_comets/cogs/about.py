import logging

import discord
from discord import Embed, app_commands
from discord.ext import commands

from courageous_comets import __version__

logger = logging.getLogger(__name__)

DESCRIPTION = """
%s

Click the link in the header to visit the documentation!
"""


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
            embed = Embed(
                title=f"Courageous Comets ({__version__})",
                description=self.description,
                color=discord.Color.blurple(),
                url=f"https://thijsfranck.github.io/courageous-comets/{__version__}/",
                timestamp=discord.utils.utcnow(),
            )

            footer_text = f"Generated using Courageous Comets {__version__}"

            embed.set_footer(text=footer_text)

            await interaction.response.send_message(
                embed=embed,
                ephemeral=True,
            )
        except discord.HTTPException as e:
            logger.exception("Could not deliver the about message.", exc_info=e)

    @property
    def description(self) -> str:
        """Return the body of the about message."""
        return DESCRIPTION % self.bot.description


async def setup(bot: commands.Bot) -> None:
    """Load the cog."""
    await bot.add_cog(About(bot))
