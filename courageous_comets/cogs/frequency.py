import discord
from discord import app_commands
from discord.ext import commands

from courageous_comets.client import CourageousCometsBot
from courageous_comets.enums import Duration
from courageous_comets.redis.messages import get_messages_frequency
from courageous_comets.ui.charts import frequency_line
from courageous_comets.ui.embeds import message_frequency


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
        duration: Duration,
    ) -> None:
        """
        Allow users to view the frequency of messages.

        Generates an embed of a graph of number of messages over duration.

        Parameters
        ----------
        interaction: discord.Interaction
            The interaction that triggered the command.
        duration: courageous_comets.enums.Duration
            The duration over which to aggregate the number of messages.
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

        if duration not in Duration:
            return await interaction.response.send_message(
                "Invalid duration provided.",
                ephemeral=True,
            )

        frequencies = await get_messages_frequency(
            self.bot.redis,
            guild_id=str(interaction.guild.id),
            duration=duration,
        )

        if not frequencies:
            return await interaction.response.send_message(
                "No messages were found over the specified duration at this time.",
                ephemeral=True,
            )

        embed = message_frequency.render(frequencies, duration)

        chart = frequency_line.render(frequencies, duration)
        embed.set_image(url=f"attachment://{chart.filename}")

        return await interaction.response.send_message(
            embed=embed,
            file=chart,
            ephemeral=True,
        )


async def setup(bot: CourageousCometsBot) -> None:
    """Load the cog."""
    await bot.add_cog(Frequency(bot))
