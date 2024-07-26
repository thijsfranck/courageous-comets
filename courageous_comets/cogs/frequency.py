import io

import discord
import matplotlib.pyplot as plt
from discord import app_commands
from discord.ext import commands
from matplotlib.dates import (
    AutoDateLocator,
    ConciseDateFormatter,
    DayLocator,
    HourLocator,
    MinuteLocator,
)

from courageous_comets import models
from courageous_comets.client import CourageousCometsBot
from courageous_comets.enums import Duration
from courageous_comets.redis.messages import get_messages_frequency


def plot_message_frequency(
    frequencies: list[models.MessageFrequency],
    duration: Duration,
) -> io.BytesIO:
    """
    Plot the frequency of messages.

    Creates a line plot of number of messages over intervals and saves it to a file.

    Parameters
    ----------
    frequencies: list[MessageFrequency]
        A list of message frequency.

    Returns
    -------
    io.BytesIO
        A plot of the frequency in memory.

    Note
    ----
    Assumes list of frequencies is not empty.
    """
    _, ax = plt.subplots()
    # If the there's only one point, use a bar plot, otherwise a line plot
    if len(frequencies) > 1:
        ax.plot(
            [frequency.timestamp for frequency in frequencies],  # type: ignore
            [frequency.num_messages for frequency in frequencies],
        )
        locator = AutoDateLocator().get_locator(
            frequencies[0].timestamp,
            frequencies[-1].timestamp,
        )
    else:
        ax.bar([frequencies[0].timestamp], [frequencies[0].num_messages], width=0.01)  # type: ignore
        if duration == Duration.daily:
            locator = DayLocator()
        elif duration == Duration.hourly:
            locator = HourLocator()
        elif duration == Duration.minute:
            locator = MinuteLocator()
        else:
            locator = AutoDateLocator()
    formatter = ConciseDateFormatter(locator)

    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)

    ax.set_ylabel("Number of messages.")
    ax.set_title("Message Frequency")

    file = io.BytesIO()
    plt.savefig(file)
    file.seek(0)

    return file


class Frequency(commands.Cog):
    """Frequency related commands."""

    def __init__(self, bot: CourageousCometsBot) -> None:
        self.bot = bot

        for attribute in dir(self):
            obj = getattr(self, attribute, None)
            if obj and getattr(obj, "is_contextmenu", False):
                menu = app_commands.ContextMenu(name=obj.name, callback=obj)
                self.bot.tree.add_command(menu)

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
        view = discord.Embed(
            title="Message frequencies",
            description="Message frequencies",
            color=discord.Colour.purple(),
            timestamp=discord.utils.utcnow(),
        )
        chart = plot_message_frequency(frequencies, duration)
        chart_file = discord.File(chart, filename="frequency.png")
        view.set_image(url="attachment://frequency.png")

        return await interaction.response.send_message(
            embed=view,
            file=chart_file,
            ephemeral=True,
        )


async def setup(bot: CourageousCometsBot) -> None:
    """Load the cog."""
    await bot.add_cog(Frequency(bot))
