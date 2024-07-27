import io

import discord
import matplotlib.pyplot as plt
from matplotlib.dates import (
    AutoDateLocator,
    ConciseDateFormatter,
    DayLocator,
    HourLocator,
    MinuteLocator,
)

from courageous_comets import models
from courageous_comets.enums import Duration


def render(
    frequencies: list[models.MessageFrequency],
    duration: Duration,
) -> discord.File:
    """
    Plot the frequency of messages.

    Creates a line plot of number of messages over intervals and saves it to a file.

    Parameters
    ----------
    frequencies: list[MessageFrequency]
        A list of message frequency.

    Returns
    -------
    discord.File
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

    formatter = ConciseDateFormatter(locator)

    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)

    ax.set_ylabel("Number of messages.")
    ax.set_title("Message Frequency")

    file_ = io.BytesIO()
    plt.savefig(file_)
    file_.seek(0)

    return discord.File(file_, filename="message_frequency.png")
