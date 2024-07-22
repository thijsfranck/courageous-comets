import logging

import discord
from discord.ext import commands

from courageous_comets.client import CourageousCometsBot
from courageous_comets.models import MessageAnalysis
from courageous_comets.redis import messages
from courageous_comets.sentiment import calculate_sentiment
from courageous_comets.vectorizer import Vectorizer

logger = logging.getLogger(__name__)


class Messages(commands.Cog):
    """A cog that listens for messages from discord."""

    def __init__(self, bot: CourageousCometsBot) -> None:
        self.bot = bot
        self.vectorizer = Vectorizer()

    @commands.Cog.listener(name="on_message")
    async def on_message(self, message: discord.Message) -> None:
        """
        When a message is received, save it to Redis.

        Parameters
        ----------
        message : discord.Message
            The message to save.
        """
        await self.save_message(message)

    async def save_message(self, message: discord.Message) -> None:
        """
        Save a message on Redis.

        Ignore messages that are not in a guild or if the bot is not connected to Redis.

        Parameters
        ----------
        message : discord.Message
            The message to save.
        """
        if not self.bot.redis:
            return logger.warning(
                "Ignoring message %s because the bot is not connected to Redis",
                message.id,
            )
        # Ignore empty messages
        if not message.content:
            logger.warning("Ignoring empty message %s", message.id)
            return None

        # Extract the IDs from the message
        guild_id = message.guild.id if message.guild else 0
        channel_id = message.channel.id if message.channel else 0
        user_id = message.author.id if message.author else 0
        message_id = message.id if message.id else 0

        # Ignore messages without all required IDs
        if not all((guild_id, channel_id, user_id, message_id)):
            logger.warning("Ignoring message %s with missing IDs", message.id)
            return None

        embedding = await self.vectorizer.aencode(message.content)

        key = await messages.save_message(
            self.bot.redis,
            MessageAnalysis(
                user_id=str(message.author.id),
                message_id=str(message.id),
                channel_id=str(message.channel.id),
                guild_id=str(message.guild.id),  # pyright: ignore
                timestamp=message.created_at,
                embedding=embedding,
                sentiment=calculate_sentiment(message.content),
            ),
        )

        return logger.info(
            "Saved message %s to Redis with key %s",
            message.id,
            key,
        )


async def setup(bot: CourageousCometsBot) -> None:
    """
    Load the cog.

    Parameters
    ----------
    bot : CourageousCometsBot
        The bot instance.
    """
    await bot.add_cog(Messages(bot))
