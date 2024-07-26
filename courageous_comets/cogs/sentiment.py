from pathlib import Path

import discord
import matplotlib.pyplot as plt
from discord import app_commands
from discord.ext import commands

from courageous_comets.client import CourageousCometsBot
from courageous_comets.enums import StatisticScope
from courageous_comets.redis.keys import key_schema
from courageous_comets.redis.messages import (
    get_message_sentiment,
    get_messages_by_sentiment_similarity,
)
from courageous_comets.utils import contextmenu
from courageous_comets.vectorizer import Vectorizer


class MessagesNotFound(app_commands.AppCommandError):
    """No messages were found."""


def plot_sentiment_analysis(message_id: str | int, analysis_result: dict[str, float]) -> Path:
    """
    Plot the sentiment analysis of a message.

    Creates a bar chart of the sentiment analysis of a message and saves it to a file.
    If the file already exists, it will be returned instead of being recreated.

    Parameters
    ----------
    message_id : str | int
        The id of the message.
    analysis_result : MessageAnalysis
        The result of sentiment analysis on a message.

    Returns
    -------
    Path
        The path to the saved image.
    """
    chart_dir = Path("artifacts/charts/sentiment").resolve()

    if not chart_dir.exists():
        chart_dir.mkdir(parents=True, exist_ok=True)

    chart_path = chart_dir / f"{message_id}.png"

    if chart_path.exists():
        return chart_path

    _, ax = plt.subplots()
    ax.bar(
        [
            "Negative",
            "Neutral",
            "Positive",
        ],
        [
            analysis_result["sentiment_neg"],
            analysis_result["sentiment_neu"],
            analysis_result["sentiment_pos"],
        ],
        color=[
            "red",
            "blue",
            "green",
        ],
    )
    ax.set_ylabel("Sentiment Score")
    ax.set_title("Sentiment Analysis")

    plt.savefig(chart_path)

    return chart_path


class Sentiment(commands.Cog):
    """Sentiment related commands."""

    def __init__(self, bot: CourageousCometsBot) -> None:
        self.bot = bot

        self.vectorizer = Vectorizer()

        for attribute in dir(self):
            obj = getattr(self, attribute, None)
            if obj and getattr(obj, "is_contextmenu", False):
                menu = app_commands.ContextMenu(name=obj.name, callback=obj)
                self.bot.tree.add_command(menu)

    @contextmenu(name="Show message sentiment")
    async def show_message_sentiment(
        self,
        interaction: discord.Interaction,
        message: discord.Message,
    ) -> None:
        """Show the sentiment of a message."""
        if self.bot.redis is None:
            return await interaction.response.send_message(
                "This feature is currently unavailable. Please try again later.",
                ephemeral=True,
            )

        if message.guild is None:
            return await interaction.response.send_message(
                "This feature is only available in guilds.",
                ephemeral=True,
            )

        key = key_schema.guild_messages(guild_id=message.guild.id, message_id=message.id)

        analysis_result = await get_message_sentiment(key, redis=self.bot.redis)

        if analysis_result is None:
            return await interaction.response.send_message(
                "No sentiment analysis found for this message.",
                ephemeral=True,
            )

        color = (
            discord.Color.green()
            if analysis_result["sentiment_compound"] >= 0
            else discord.Color.red()
        )

        view = discord.Embed(
            title="Message Sentiment",
            description=f"Sentiment analysis of message with ID {message.id}",
            color=color,
            timestamp=discord.utils.utcnow(),
            type="rich",
        )

        chart = plot_sentiment_analysis(message.id, analysis_result)
        chart_file = discord.File(chart, filename="sentiment_analysis.png")
        view.set_image(url="attachment://sentiment_analysis.png")

        return await interaction.response.send_message(
            embed=view,
            file=chart_file,
            ephemeral=True,
        )

    @contextmenu(name="Show similar sentiment")
    async def get_similar_messages(
        self,
        interaction: discord.Interaction,
        message: discord.Message,
    ) -> None:
        """Get similar messages based on semantics."""
        if self.bot.redis is None:
            return await interaction.response.send_message(
                "This feature is currently unavailable. Please try again later.",
                ephemeral=True,
            )

        await interaction.response.defer()

        embedding = await self.vectorizer.aencode(message.content)

        messages = await get_messages_by_sentiment_similarity(
            self.bot.redis,
            message.guild.id,  # type: ignore
            embedding,
            StatisticScope.GUILD,
        )

        if not messages:
            raise MessagesNotFound

        # TODO(isaa-ctaylor): Display messages
        return None


async def setup(bot: CourageousCometsBot) -> None:
    """Load the cog."""
    await bot.add_cog(Sentiment(bot))
