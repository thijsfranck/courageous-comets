import discord
from discord import app_commands
from discord.ext import commands

from courageous_comets.client import CourageousCometsBot
from courageous_comets.enums import StatisticScope
from courageous_comets.redis.messages import get_messages_by_semantics_similarity
from courageous_comets.utils import contextmenu
from courageous_comets.vectorizer import Vectorizer


class MessagesNotFound(app_commands.AppCommandError):
    """No messages were found."""


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

    @contextmenu(name="Show Sentiment")
    async def _get_message_similarities(
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

        messages = await get_messages_by_semantics_similarity(
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
