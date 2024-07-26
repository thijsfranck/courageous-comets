import discord
from discord import app_commands
from discord.ext import commands

from courageous_comets.client import CourageousCometsBot


class Frequency(commands.Cog):
    """Frequency related commands."""

    def __init__(self, bot: CourageousCometsBot) -> None:
        self.bot = bot

    @app_commands.command(
        name="frequency",
        description="Get frequency of messages over a duration.",
    )
    async def frequency_command(
        self,
        interaction: discord.Interaction,
    ) -> None:
        """
        Allow users to view the frequency of messages.

        Generates an embed of a graph of number of messages over duration.

        Parameters
        ----------
        interaction: discord.Interaction
            The interaction that triggered the command.
        duration: courageous_comets.enums.Duration
            The duration to calculate the number of messages.
        """
        if self.bot.redis is None:
            return await interaction.response.send_message(
                "This feature is currently unavailable. Please try again later.",
                ephemeral=True,
            )

        if interaction.guild is None:
            return await interaction.response.send_message(
                "This feature is only available in guilds.",
                ephemeral=True,
            )
        return await interaction.response.send_message(
            "This feature is currently unavailable. Please try again later.",
            ephemeral=True,
        )


async def setup(bot: CourageousCometsBot) -> None:
    """Load the cog."""
    await bot.add_cog(Frequency(bot))
