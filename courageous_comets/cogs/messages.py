import logging

import discord
from discord.ext import commands
from redis.asyncio import Redis

from courageous_comets.client import CourageousCometsBot
from courageous_comets.models import VectorizedMessage
from courageous_comets.redis import messages
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
        Save a message to the database.

        If the bot is not connected to Redis, this method does nothing.

        Parameters
        ----------
        message : discord.Message
            The message to save.
        """
        if not self.bot.redis:
            return

        await save_message(message, self.bot.redis, self.vectorizer)


async def setup(bot: CourageousCometsBot) -> None:
    """
    Load the cog.

    Parameters
    ----------
    bot : CourageousCometsBot
        The bot instance.
    """
    await bot.add_cog(Messages(bot))


async def save_message(message: discord.Message, redis: Redis, vectorizer: Vectorizer) -> None:
    """
    Save a message on Redis.

    Parameters
    ----------
    message : discord.Message
        The message to save.
    redis: Redis
        The Redis connection instance.
    vectorizer : Vectorizer
        The vectorizer to use to embed the message.

    Returns
    -------
    str
        The key to the data on Redis.
    """
    if not message.guild:
        return logger.debug("Ignoring message %s because it's not in a guild", message.id)

    embedding = await vectorizer.embed(message.content)

    vectorized_message = VectorizedMessage(
        user_id=str(message.author.id),
        message_id=str(message.id),
        channel_id=str(message.channel.id),
        guild_id=str(message.guild.id),
        content=message.content,
        timestamp=message.created_at,
        embedding=embedding,
    )

    key = await messages.save_message(redis, vectorized_message)

    return logger.debug("Saved message %s to Redis with key %s", message.id, key)
