import logging

import discord
from discord import app_commands
from discord.ext import commands

from courageous_comets.charts import plot_sentiment_analysis
from courageous_comets.client import CourageousCometsBot
from courageous_comets.enums import StatisticScope
from courageous_comets.redis.keys import key_schema
from courageous_comets.redis.messages import (
    get_message_sentiment,
    get_messages_by_sentiment_similarity,
)
from courageous_comets.sentiment import calculate_sentiment
from courageous_comets.utils import contextmenu
from courageous_comets.vectorizer import Vectorizer

logger = logging.getLogger(__name__)


class MessagesNotFound(app_commands.AppCommandError):
    """No messages were found."""


SENTIMENT: dict[range, str] = {
    range(-100, -50): "very negative 😡",
    range(-50, -10): "negative 🙁",
    range(-10, 10): "neutral 🙂",
    range(10, 50): "positive 😁",
    range(50, 100): "very positive 😍",
}


SENTIMENT_DESCRIPTION_TEMPLATE = """
Overall the sentiment of the message is **{sentiment}**.

Here's a breakdown of the scores:

- Negative: {neg}
- Neutral: {neu}
- Positive: {pos}

The compound score is {compound}.
"""


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
        """
        Allow users to view the sentiment analysis of a message using a context menu.

        Generates an embed with the sentiment analysis of a message and sends it to the user.

        The embed contains a text description of the sentiment analysis and a bar chart.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction that triggered the command.
        message : discord.Message
            The message to analyze.
        """
        logger.info(
            "User %s requested sentiment analysis results for message %s.",
            interaction.user.id,
            message.id,
        )

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

        key = key_schema.guild_messages(
            guild_id=message.guild.id,
            message_id=message.id,
        )

        analysis_result = await get_message_sentiment(key, redis=self.bot.redis)

        if analysis_result is None:
            return await interaction.response.send_message(
                "No sentiment analysis found for this message.",
                ephemeral=True,
            )

        color = discord.Color.green() if analysis_result.compound >= 0 else discord.Color.red()

        sentiment = next(
            (
                value
                for key, value in SENTIMENT.items()
                if int(analysis_result.compound * 100) in key
            ),
            "unknown",
        )

        template_vars = {
            **analysis_result.model_dump(),
            "sentiment": sentiment,
        }

        embed = discord.Embed(
            title="Message Sentiment",
            description=SENTIMENT_DESCRIPTION_TEMPLATE.format(**template_vars),
            color=color,
            timestamp=discord.utils.utcnow(),
        )

        chart = plot_sentiment_analysis(message.id, analysis_result)
        chart_file = discord.File(chart, filename="sentiment_analysis.png")
        embed.set_image(url="attachment://sentiment_analysis.png")

        return await interaction.response.send_message(
            embed=embed,
            file=chart_file,
            ephemeral=True,
        )

    @contextmenu(name="Show similar sentiment")
    async def get_similar_messages(
        self,
        interaction: discord.Interaction,
        message: discord.Message,
    ) -> None:
        """
        Allow users to view the sentiment analysis of a message using a context menu.

        Generates an embed with the sentiment analysis of a message and sends it to the user.

        The embed contains a text description of the sentiment analysis and a bar chart.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction that triggered the command.
        message : discord.Message
            The message to analyze.
        """
        logger.info(
            "User %s requested sentiment analysis results for message %s.",
            interaction.user.id,
            message.id,
        )

        if self.bot.redis is None:
            return await interaction.response.send_message(
                "This feature is currently unavailable. Please try again later.",
                ephemeral=True,
            )

        await interaction.response.defer()

        sentiment = calculate_sentiment(message.content)
        messages = await get_messages_by_sentiment_similarity(
            self.bot.redis,
            guild_id=str(message.guild.id),  # type: ignore
            sentiment=sentiment.compound,
            scope=StatisticScope.GUILD,
            radius=0.1,
        )

        if not messages:
            raise MessagesNotFound

        # TODO(isaa-ctaylor): Display messages
        return None


async def setup(bot: CourageousCometsBot) -> None:
    """Load the cog."""
    await bot.add_cog(Sentiment(bot))
