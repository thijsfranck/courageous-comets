import logging

import discord
from discord import app_commands
from discord.ext import commands

from courageous_comets import preprocessing
from courageous_comets.client import CourageousCometsBot
from courageous_comets.discord.messages import resolve_messages
from courageous_comets.redis.messages import get_messages_by_sentiment_similarity
from courageous_comets.sentiment import calculate_sentiment
from courageous_comets.ui.embeds import search_results

logger = logging.getLogger(__name__)


class SentimentSearchCommand(commands.Cog):
    """
    A cog that provides sentiment search using a the /sentiment_search command.

    Attributes
    ----------
    bot : CourageousCometsBot
        The bot instance.
    """

    def __init__(self, bot: CourageousCometsBot) -> None:
        self.bot = bot

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
            "User %s requested search by sentiment %s using a custom query.",
            interaction.user.id,
            interaction.id,
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

        if interaction.guild is None:
            logger.debug(
                "Could not answer sentiment request %s due to not being triggered from a guild.",
                interaction.id,
            )
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
            logger.debug("No data found for sentiment request %s.", interaction.id)
            return await interaction.followup.send(
                "No related messages were found.",
                ephemeral=True,
            )

        embed = search_results.render(query, resolved_messages)

        logger.debug("Sending sentiment analysis results for %s.", interaction.id)

        return await interaction.followup.send(embed=embed, ephemeral=True)


async def setup(bot: CourageousCometsBot) -> None:
    """Load the cog."""
    await bot.add_cog(SentimentSearchCommand(bot))
