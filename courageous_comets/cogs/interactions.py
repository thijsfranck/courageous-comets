import typing

import discord
from discord import app_commands
from discord.ext import commands

from courageous_comets.client import CourageousCometsBot
from courageous_comets.models import Message
from courageous_comets.redis.messages import get_similar_messages
from courageous_comets.vectorizer import Vectorizer


class MessagesNotFound(app_commands.AppCommandError):
    """No messages were found."""


def contextmenu(name: str) -> typing.Callable:
    """Mark a function as a context menu."""

    def wrap(func: typing.Callable) -> typing.Callable:
        func.is_contextmenu = True
        func.name = name
        return func

    return wrap


class Interactions(commands.Cog):
    """A boilerplate cog."""

    def __init__(self, bot: CourageousCometsBot) -> None:
        self.bot = bot

        self.vectorizer = Vectorizer()

        for attribute in dir(self):
            obj = getattr(self, attribute, None)
            if obj and getattr(obj, "is_contextmenu", False):
                menu = app_commands.ContextMenu(name=obj.name, callback=obj)
                self.bot.tree.add_command(menu)

    @contextmenu(name="Show similar messages")
    async def _get_message_similarities(
        self,
        interaction: discord.Interaction,
        message: discord.Message,
    ) -> None:
        """Get similar messages based on semantics."""
        # TODO(isaa-ctaylor): interaction checks
        # TODO(isaa-ctaylor): check redis connection
        await interaction.response.defer()

        embedding = await self.vectorizer.aencode(message.content)
        model_message = Message(
            user_id=str(message.author.id),
            message_id=str(message.id),
            channel_id=str(message.channel.id),
            guild_id=str(message.guild.id),  # type: ignore
            content=message.content,
            timestamp=message.created_at,
        )

        messages = await get_similar_messages(self.bot.redis, model_message, embedding)  # type: ignore

        if not messages:
            raise MessagesNotFound

        # TODO(isaa-ctaylor): Display messages


async def setup(bot: CourageousCometsBot) -> None:
    """Load the cog."""
    await bot.add_cog(Interactions(bot))
