import logging

import discord
from discord import app_commands
from discord.ext import commands

from courageous_comets.client import CourageousCometsBot
from courageous_comets.discord.messages import resolve_messages
from courageous_comets.preprocessing import process
from courageous_comets.redis.messages import get_messages_by_semantics_similarity
from courageous_comets.ui.embeds import search_results
from courageous_comets.utils import contextmenu
from courageous_comets.vectorizer import Vectorizer

logger = logging.getLogger(__name__)


class MessagesNotFound(app_commands.AppCommandError):
    """No messages were found."""


class Keywords(commands.Cog):
    """A boilerplate cog."""

    def __init__(self, bot: CourageousCometsBot) -> None:
        self.bot = bot
        self.vectorizer = Vectorizer()

        for attribute in dir(self):
            obj = getattr(self, attribute, None)
            if obj and getattr(obj, "is_contextmenu", False):
                menu = app_commands.ContextMenu(name=obj.name, callback=obj)
                self.bot.tree.add_command(menu)

    @app_commands.command(name="search", description="Search for related messages.")
    async def search_by_topic(self, interaction: discord.Interaction, query: str) -> None:
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
            "User %s requested a search for related messages using the /search command.",
            interaction.user.id,
        )

        if self.bot.redis is None:
            return await interaction.response.send_message(
                "This feature is currently unavailable. Please try again later.",
                ephemeral=True,
            )

        if not interaction.guild:
            return await interaction.response.send_message(
                "This command can only be used in a guild.",
                ephemeral=True,
            )

        if not interaction.channel:
            return await interaction.response.send_message(
                "This command can only be used in a channel.",
                ephemeral=True,
            )

        if not query:
            return await interaction.response.send_message(
                "Please provide a query to search for related messages.",
                ephemeral=True,
            )

        await interaction.response.defer(ephemeral=True, thinking=True)

        query_processed = process(query)
        query_vector = await self.vectorizer.aencode(query_processed)

        messages = await get_messages_by_semantics_similarity(
            self.bot.redis,
            guild_id=str(interaction.guild.id),
            embedding=query_vector,
            limit=5,
        )

        resolved_messages = await resolve_messages(self.bot, messages)

        if not resolved_messages:
            return await interaction.followup.send("No related messages were found.")

        embed = search_results.render(query, resolved_messages)

        return await interaction.followup.send(embed=embed)

    @contextmenu(name="Search by topic")
    async def search_by_topic_with_message(
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
            "User %s requested search by sentiment for message %s.",
            interaction.user.id,
            message.id,
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

        query_processed = process(message.clean_content)
        query_vector = await self.vectorizer.aencode(query_processed)

        messages = await get_messages_by_semantics_similarity(
            self.bot.redis,
            guild_id=str(interaction.guild.id),
            embedding=query_vector,
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
    await bot.add_cog(Keywords(bot))
