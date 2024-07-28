import logging

import discord
from discord import app_commands
from discord.ext import commands

from courageous_comets.client import CourageousCometsBot
from courageous_comets.processing import process_message
from courageous_comets.redis.keys import key_schema
from courageous_comets.redis.messages import get_message_sentiment
from courageous_comets.ui.charts import sentiment_bars
from courageous_comets.ui.embeds import message_sentiment
from courageous_comets.ui.views.sentiment import SentimentView

logger = logging.getLogger(__name__)


class SentimentMessageContextMenu(commands.Cog):
    """
    A cog that provides sentiment analysis for a message using a context menu.

    Attributes
    ----------
    bot : CourageousCometsBot
        The bot instance.
    """

    def __init__(self, bot: CourageousCometsBot) -> None:
        self.bot = bot

        menu = app_commands.ContextMenu(
            name="Show message sentiment",
            callback=self.show_message_sentiment,
        )
        self.bot.tree.add_command(menu)

    async def show_message_sentiment(
        self,
        interaction: discord.Interaction,
        message: discord.Message,
    ) -> None:
        """
        Allow users to view the sentiment analysis of a message using a context menu.

        Generates an embed with the sentiment analysis of a message and sends it to the user.

        The embed contains a text description of the sentiment analysis and a bar chart.
        A view is attached to the message to allow users to interact with the sentiment analysis.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction that triggered the command.
        message : discord.Message
            The message to analyze.
        """
        logger.info(
            "User %s requested sentiment analysis results %s for message %s.",
            interaction.user.id,
            interaction.id,
            message.id,
        )

        if self.bot.redis is None:
            logger.error(
                "Could not answer sentiment request %s due to Redis being unavailable.",
                interaction.id,
            )
            return await interaction.response.send_message(
                "This feature is currently unavailable. Please try again later.",
                ephemeral=True,
            )

        if message.guild is None:
            logger.debug(
                "Could not answer sentiment request %s due to not message being from a guild.",
                interaction.id,
            )
            return await interaction.response.send_message(
                "This feature is only available in guilds.",
                ephemeral=True,
            )

        await interaction.response.defer(ephemeral=True, thinking=True)

        key = key_schema.guild_messages(
            guild_id=message.guild.id,
            message_id=message.id,
        )

        if not await self.bot.redis.exists(key):
            logger.debug("Message %s is not previously saved. Processing it.", message.id)
            await process_message(
                message,
                redis=self.bot.redis,
                vectorizer=self.bot.vectorizer,
            )

        analysis_result = await get_message_sentiment(key, redis=self.bot.redis)

        if analysis_result is None:
            logger.debug("No data found for sentiment request %s.", interaction.id)
            return await interaction.followup.send(
                "No analysis results were found.",
                ephemeral=True,
            )

        embed = message_sentiment.render(analysis_result)

        chart = sentiment_bars.for_message(message.id, analysis_result)
        embed.set_image(url=f"attachment://{chart.filename}")

        view = SentimentView(message.author, analysis_result)

        logger.debug("Sending sentiment analysis results for %s.", interaction.id)

        return await interaction.followup.send(
            embed=embed,
            file=chart,
            view=view,
            ephemeral=True,
        )


async def setup(bot: CourageousCometsBot) -> None:
    """Load the cog."""
    await bot.add_cog(SentimentMessageContextMenu(bot))
