import logging

import discord
from discord import app_commands
from discord.ext import commands

from courageous_comets import preprocessing
from courageous_comets.client import CourageousCometsBot
from courageous_comets.discord.messages import resolve_messages
from courageous_comets.enums import StatisticScope
from courageous_comets.processing import process_message
from courageous_comets.redis.keys import key_schema
from courageous_comets.redis.messages import (
    get_average_sentiment,
    get_message_sentiment,
    get_messages_by_sentiment_similarity,
)
from courageous_comets.sentiment import calculate_sentiment
from courageous_comets.ui.charts import sentiment_bars
from courageous_comets.ui.embeds import message_sentiment, search_results, user_sentiment
from courageous_comets.utils import contextmenu

logger = logging.getLogger(__name__)


class MessagesNotFound(app_commands.AppCommandError):
    """No messages were found."""


class Sentiment(commands.Cog):
    """Sentiment related commands."""

    def __init__(self, bot: CourageousCometsBot) -> None:
        self.bot = bot

        for attribute in dir(self):
            obj = getattr(self, attribute, None)
            if obj and getattr(obj, "is_contextmenu", False):
                menu = app_commands.ContextMenu(name=obj.name, callback=obj)
                self.bot.tree.add_command(menu)

    @contextmenu(name="Show user sentiment")
    async def show_user_sentiment(
        self,
        interaction: discord.Interaction,
        user: discord.User | discord.Member,
    ) -> None:
        """
        Allow users to view the sentiment analysis of a user using a context menu.

        Generates an embed with the sentiment analysis of a user and sends it to the user.
        The embed contains a line chart of the sentiment of a user over time.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction that triggered the command.
        user : discord.User | discord.Member
            The user to analyze.
        """
        logger.info(
            "User %s requested sentiment analysis results for user %s.",
            interaction.user.id,
            user.id,
        )

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

        await interaction.response.defer(ephemeral=True, thinking=True)

        sentiment_results = await get_average_sentiment(
            redis=self.bot.redis,
            guild_id=str(interaction.guild.id),
            ids=[str(user.id)],
            scope=StatisticScope.USER,
        )

        if not sentiment_results:
            await interaction.followup.send(
                f"No sentiment data found for {user.mention}.",
                ephemeral=True,
            )

        average_sentiment = sentiment_results[0]

        embed = user_sentiment.render(user, average_sentiment)

        chart = sentiment_bars.for_user(average_sentiment)
        embed.set_image(url=f"attachment://{chart.filename}")

        return await interaction.followup.send(
            embed=embed,
            file=chart,
            ephemeral=True,
        )

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
            logger.warning("Could not find analysis result for message %s.", message.id)
            return await interaction.followup.send(
                "No analysis results were found.",
                ephemeral=True,
            )

        embed = message_sentiment.render(analysis_result)

        chart = sentiment_bars.for_message(message.id, analysis_result)
        embed.set_image(url=f"attachment://{chart.filename}")

        return await interaction.followup.send(embed=embed, file=chart, ephemeral=True)

    @app_commands.command(
        name="sentiment_search",
        description="Search for messages with similar sentiment.",
    )
    async def search_by_sentiment(
        self,
        interaction: discord.Interaction,
        query: str,
    ) -> None:
        """
        Allow users to search for messages with similar sentiment using a context menu.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction that triggered the command.
        query : str
            The message to use as a reference for the search
        """
        logger.info(
            "User %s requested search by sentiment using a custom query.",
            interaction.user.id,
        )

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

        await interaction.response.defer(ephemeral=True, thinking=True)

        prepared_content = preprocessing.process(query)
        sentiment = calculate_sentiment(prepared_content)

        messages = await get_messages_by_sentiment_similarity(
            self.bot.redis,
            guild_id=str(interaction.guild.id),
            sentiment=sentiment.compound,
            radius=0.1,
            limit=5,
        )

        resolved_messages = await resolve_messages(self.bot, messages)

        if not resolved_messages:
            return await interaction.followup.send(
                "No related messages were found.",
                ephemeral=True,
            )

        embed = search_results.render(query, resolved_messages)

        return await interaction.followup.send(embed=embed, ephemeral=True)

    @contextmenu(name="Search by sentiment")
    async def search_by_sentiment_with_message(
        self,
        interaction: discord.Interaction,
        message: discord.Message,
    ) -> None:
        """
        Allow users to search for messages with similar sentiment using a context menu.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction that triggered the command.
        message : discord.Message
            The message to use as a reference for the search.
        """
        logger.info(
            "User %s requested search by sentiment for message %s.",
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
            logger.warning("Could not find analysis result for message %s.", message.id)
            return await interaction.followup.send(
                "No related messages were found.",
                ephemeral=True,
            )

        messages = await get_messages_by_sentiment_similarity(
            self.bot.redis,
            guild_id=str(message.guild.id),
            sentiment=analysis_result.compound,
            radius=0.1,
            limit=6,
        )

        resolved_messages = [
            resolved_message
            for resolved_message in await resolve_messages(self.bot, messages)
            if resolved_message.id != message.id
        ]

        if not resolved_messages:
            return await interaction.followup.send(
                "No related messages were found.",
                ephemeral=True,
            )

        embed = search_results.render(message.clean_content, resolved_messages)

        return await interaction.followup.send(embed=embed, ephemeral=True)


async def setup(bot: CourageousCometsBot) -> None:
    """Load the cog."""
    await bot.add_cog(Sentiment(bot))
