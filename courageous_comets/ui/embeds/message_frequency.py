import discord

from courageous_comets import models
from courageous_comets.enums import Duration
from courageous_comets.ui.embeds import format_embed

DURATION_NAME = {
    Duration.daily: "day",
    Duration.hourly: "hour",
    Duration.minute: "minute",
}

TEMPLATE = """
The chart below shows the number of messages sent by users on this server per **{duration}**.

Times shown in the chart are in UTC.
"""


def render(frequencies: list[models.MessageFrequency], duration: Duration) -> discord.Embed:
    """
    Render the frequency of messages.

    Creates an embed of the frequency of messages over intervals.

    Parameters
    ----------
    frequencies: list[MessageFrequency]
        A list of message frequency.

    Returns
    -------
    discord.Embed
        An embed of the frequency.
    """
    template_vars = {
        "duration": DURATION_NAME[duration],
    }

    embed = discord.Embed(
        title="Message Frequency",
        description=TEMPLATE.format_map(template_vars),
        color=discord.Colour.purple(),
        timestamp=discord.utils.utcnow(),
    )

    total_messages = sum(frequency.num_messages for frequency in frequencies)
    peak_frequency = max(frequencies, key=lambda frequency: frequency.num_messages)

    time_style = "D" if duration == Duration.daily else "t"
    most_active_time = discord.utils.format_dt(peak_frequency.timestamp, style=time_style)

    embed.add_field(
        name="Total",
        value=total_messages,
        inline=True,
    )

    embed.add_field(
        name="Peak",
        value=peak_frequency.num_messages,
        inline=True,
    )

    embed.add_field(
        name="Most active time",
        value=most_active_time,
        inline=True,
    )

    return format_embed(embed)
