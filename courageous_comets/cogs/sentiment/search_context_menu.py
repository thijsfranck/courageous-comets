import logging

import discord
from discord import app_commands
from discord.ext import commands

from courageous_comets.client import CourageousCometsBot
from courageous_comets.discord.messages import resolve_messages
from courageous_comets.processing import process_message
from courageous_comets.redis.keys import key_schema
from courageous_comets.redis.messages import (
    get_message_sentiment,
    get_messages_by_sentiment_similarity,
)
from courageous_comets.ui.embeds import search_results

logger = logging.getLogger(__name__)


class SentimentSearchContextMenu(commands.Cog):
    """
    A cog that provides sentiment search using a context menu.

    Attributes
    ----------
    bot : CourageousCometsBot
        The bot instance.
    """

    def __init__(self, bot: CourageousCometsBot) -> None:
        self.bot = bot

        menu = app_commands.ContextMenu(
            name="Search by sentiment",
            callback=self.search_by_sentiment,
        )
        self.bot.tree.add_command(menu)

    async def search_by_sentiment(
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
            "User %s requested search by sentiment %s for message %s.",
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
                "Could not answer sentiment request %s due to message not being from a guild.",
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
            logger.debug("No search results found for sentiment request %s.", interaction.id)
            return await interaction.followup.send(
                "No related messages were found.",
                ephemeral=True,
            )

        embed = search_results.render(message.clean_content, resolved_messages)

        logger.debug("Sending sentiment analysis results for %s.", interaction.id)

        return await interaction.followup.send(embed=embed, ephemeral=True)


async def setup(bot: CourageousCometsBot) -> None:
    """Load the cog."""
    await bot.add_cog(SentimentSearchContextMenu(bot))
