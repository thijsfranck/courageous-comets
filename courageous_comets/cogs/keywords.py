import datetime

import discord
from async_lru import alru_cache
from discord import app_commands
from discord.ext import commands

from courageous_comets.client import CourageousCometsBot
from courageous_comets.models import Message
from courageous_comets.redis.messages import get_recent_messages
from courageous_comets.vectorizer import Vectorizer

# from courageous_comets.utils import contextmenu  # noqa: ERA001


def shorten(string: str, *, limit: int = 50) -> str:
    """Trim a string if necessary given `limit`."""
    if len(string) > limit:
        string = string[: limit - 3] + "..."
    return string


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
        *,
        # user: discord.Member,
        guild_id: int,
        channels: list[discord.TextChannel],
        limit: int = 10,
    ) -> list[Message]:
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
        return await get_recent_messages(
            self.bot.redis,  # type: ignore
            guild_id=str(guild_id),
            ids=[str(channel.id) for channel in channels],
            limit=limit,
        )

    # @contextmenu(name="Show recent messages")
    # async def _show_recent_messages_context_menu(
    #     self,
    #     interaction: discord.Interaction,
    #     member: discord.Member,
    # ) -> None:
    #     """Get the most recent messages from a user."""
    #     await self._show_recent_messages(interaction, member)  # noqa: ERA001

    @app_commands.command(name="recent")
    async def _show_recent_messages_command(
        self,
        interaction: discord.Interaction,
    ) -> None:
        """Get the most recent messages in the server."""
        await self._show_recent_messages(interaction)
        # await self._show_recent_messages(interaction, member)  # noqa: ERA001

    @alru_cache()
    async def _resolve_message(self, message: Message) -> discord.Message | None:
        """
        Try and resolve a message from discord.

        Parameters
        ----------
        message: courageous_comets.models.Message
            Represents the message to resolve

        Returns
        -------
        discord.Message | None
            A `discord.Message` instance if we managed to fetch the message from discord, else None
        """
        channel: discord.TextChannel = self.bot.get_channel(int(message.channel_id))  # type: ignore
        if channel:
            resolved_message = await channel.fetch_message(int(message.message_id))
            if resolved_message:
                return resolved_message
        return None

    async def _show_recent_messages(
        self,
        interaction: discord.Interaction,
        # member: discord.Member,
    ) -> None:
        await interaction.response.defer()
        author = interaction.user

        visible_channels = [
            channel
            for channel in interaction.guild.text_channels  # type: ignore
            if channel.permissions_for(author).view_channel  # type: ignore
        ]

        messages = await self._get_recent_messages(
            guild_id=interaction.guild.id,  # type: ignore
            channels=visible_channels,
        )

        resolved_messages: list[discord.Message | None] = []

        for message in messages:
            resolved_message = await self._resolve_message(message)
            resolved_messages.append(resolved_message)

        if not [m for m in resolved_messages if m]:
            raise MessagesNotFound

        await interaction.followup.send(
            embed=discord.Embed(
                title=f"Recent messages in {interaction.guild.name}",  # type: ignore
                description="\n\n".join(
                    f"{message.author.mention} {discord.utils.format_dt(message.created_at, style='R')}:\n{shorten(message.clean_content, limit=60)}"  # noqa: E501
                    if message and message.clean_content
                    else "[Message Deleted]"
                    if not message
                    else "[No Message Content]"
                    for message in resolved_messages
                ),
                colour=discord.Colour.blurple(),
                timestamp=datetime.datetime.now(datetime.UTC),
            ),
        )


async def setup(bot: CourageousCometsBot) -> None:
    """Load the cog."""
    await bot.add_cog(Keywords(bot))
