import logging

import discord
from discord import app_commands
from discord.ext import commands

from courageous_comets import preprocessing
from courageous_comets.client import CourageousCometsBot
from courageous_comets.discord.messages import resolve_messages
from courageous_comets.redis.messages import get_messages_by_semantics_similarity
from courageous_comets.ui.embeds import search_results

logger = logging.getLogger(__name__)


class SearchCommand(commands.Cog):
    """
    A cog for the /search command.

    This cog allows users to search for related messages using the /search command.

    Attributes
    ----------
    bot : CourageousCometsBot
        The bot instance.
    """

    def __init__(self, bot: CourageousCometsBot) -> None:
        self.bot = bot

    @app_commands.command(name="search", description="Search for related messages.")
    async def search_by_topic(
        self,
        interaction: discord.Interaction,
        query: str,
    ) -> None:
        """
        Search for related messages using the /search command.

        Parameters
        ----------
        interaction : discord.Interaction
            The interaction that triggered the command.
        query : str
            The query to search for related messages.
        """
        logger.info(
            "User %s requested a search for related messages %s using the /search command.",
            interaction.user.id,
            interaction.id,
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

        if not interaction.guild:
            logger.debug(
                "Could not answer search request %s due to it being used outside of a guild.",
                interaction.id,
            )
            return await interaction.response.send_message(
                "This command can only be used in a guild.",
                ephemeral=True,
            )

        if not interaction.channel:
            logger.debug(
                "Could not answer search request %s due to it being used outside of a channel.",
                interaction.id,
            )
            return await interaction.response.send_message(
                "This command can only be used in a channel.",
                ephemeral=True,
            )

        if not query:
            logger.debug(
                "Could not answer search request %s due to it not having a query.",
                interaction.id,
            )
            return await interaction.response.send_message(
                "Please provide a query to search for related messages.",
                ephemeral=True,
            )

        await interaction.response.defer(ephemeral=True, thinking=True)

        query_processed = preprocessing.process(query)
        embedding = await self.bot.vectorizer.aencode(query_processed)

        messages = await get_messages_by_semantics_similarity(
            self.bot.redis,
            guild_id=str(interaction.guild.id),
            embedding=embedding,
            limit=5,
        )

        resolved_messages = await resolve_messages(self.bot, messages)

        if not resolved_messages:
            logger.debug("No related messages were found for search request %s.", interaction.id)
            return await interaction.followup.send("No related messages were found.")

        embed = search_results.render(query, resolved_messages)

        logger.debug("Returning search results for search request %s.", interaction.id)

        return await interaction.followup.send(embed=embed)


async def setup(bot: CourageousCometsBot) -> None:
    """Load the cog."""
    await bot.add_cog(SearchCommand(bot))
