import discord
from discord import app_commands
from discord.ext import commands

from courageous_comets.client import CourageousCometsBot
from courageous_comets.models import Message
from courageous_comets.utils import contextmenu
from courageous_comets.vectorizer import Vectorizer

# from courageous_comets.redis.messages import get_recent_messages  # noqa: ERA001


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

    async def _get_recent_messages(
        self,
        user: discord.Member,
        *,
        limit: int = 10,
        channels: list[discord.TextChannel] | None = None,
    ) -> list[Message]:  # type: ignore
        """
        Return `limit` most recent messages, only from `channels`, if provided.

        Parameters
        ----------
        user: discord.Member
            The user to get the most recent messages for.
        limit: int
            The number of messages to retrieve. Defaults to 10.
        channels: list[discord.TextChannel]
            The channels to query.
        """

    @contextmenu(name="Show recent messages")
    async def _show_recent_messages_context_menu(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
    ) -> None:
        """Get the most recent messages from a user."""
        await self._show_recent_messages(interaction, member)

    @app_commands.command(name="recent")
    async def _show_recent_messages_command(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
    ) -> None:
        """Get the most recent messages from a user."""
        await self._show_recent_messages(interaction, member)

    async def _show_recent_messages(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
    ) -> None:
        author = interaction.user

        visible_channels = [
            channel
            for channel in interaction.guild.text_channels  # type: ignore
            if channel.permissions_for(author).view_channel  # type: ignore
        ]

        messages = await self._get_recent_messages(member, channels=visible_channels)

        resolved_messages = []

        for message in messages:
            channel: discord.TextChannel = self.bot.get_channel(int(message.channel_id))  # type: ignore
            if channel:
                resolved_message = await channel.fetch_message(int(message.message_id))
                if resolved_message:
                    resolved_messages.append(resolved_message)
                    continue
            resolved_messages.append(None)

        if not [m for m in resolved_messages if m]:
            raise MessagesNotFound

        # TODO(isaa-ctaylor): Display messages


async def setup(bot: CourageousCometsBot) -> None:
    """Load the cog."""
    await bot.add_cog(Keywords(bot))
