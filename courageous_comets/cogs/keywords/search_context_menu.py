import logging

import discord
from discord import app_commands
from discord.ext import commands

from courageous_comets import preprocessing
from courageous_comets.client import CourageousCometsBot
from courageous_comets.discord.messages import resolve_messages
from courageous_comets.processing import process_message
from courageous_comets.redis.keys import key_schema
from courageous_comets.redis.messages import get_messages_by_semantics_similarity
from courageous_comets.ui.embeds import search_results

logger = logging.getLogger(__name__)


class SearchContextMenu(commands.Cog):
    """A boilerplate cog."""

    def __init__(self, bot: CourageousCometsBot) -> None:
        self.bot = bot

        menu = app_commands.ContextMenu(
            name="Search by topic",
            callback=self.search_by_topic,
        )
        self.bot.tree.add_command(menu)

    async def search_by_topic(
        self,
        interaction: discord.Interaction,
        message: discord.Message,
    ) -> None:
        """
        Search for related messages using a context menu.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction that triggered the command.
        message : discord.Message
            The message to use as a reference for the search.
        """
        logger.info(
            "User %s requested search by topic %s for message %s.",
            interaction.user.id,
            interaction.id,
            message.id,
        )

        if self.bot.redis is None:
            logger.error(
                "Could not answer search request %s due to Redis being unavailable.",
                interaction.id,
            )
            return await interaction.response.send_message(
                "This feature is currently unavailable. Please try again later.",
                ephemeral=True,
            )

        if message.guild is None:
            logger.debug(
                "Could not answer search request %s due to it being used outside of a guild.",
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

        if not self.bot.redis.exists(key):
            await process_message(
                message,
                redis=self.bot.redis,
                vectorizer=self.bot.vectorizer,
            )

        content_processed = preprocessing.process(message.clean_content)
        embedding = await self.bot.vectorizer.aencode(content_processed)

        messages = await get_messages_by_semantics_similarity(
            self.bot.redis,
            guild_id=str(message.guild.id),
            embedding=embedding,
            limit=6,
        )

        resolved_messages = [
            resolved_message
            for resolved_message in await resolve_messages(self.bot, messages)
            if resolved_message.id != message.id
        ]

        if not resolved_messages:
            logger.debug("No related messages were found for search request %s.", interaction.id)
            return await interaction.followup.send(
                "No related messages were found.",
                ephemeral=True,
            )

        embed = search_results.render(message.clean_content, resolved_messages)

        logger.debug("Returning search results for search request %s.", interaction.id)

        return await interaction.followup.send(embed=embed, ephemeral=True)


async def setup(bot: CourageousCometsBot) -> None:
    """Load the cog."""
    await bot.add_cog(SearchContextMenu(bot))
