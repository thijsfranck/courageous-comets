import logging

import discord
from discord.ext import commands

from courageous_comets import preprocessing
from courageous_comets.client import CourageousCometsBot
from courageous_comets.models import MessageAnalysis
from courageous_comets.redis import messages
from courageous_comets.sentiment import calculate_sentiment
from courageous_comets.vectorizer import Vectorizer
from courageous_comets.words import tokenize_sentence, word_frequency

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

        if not message.guild:
            return logger.debug(
                "Ignoring message %s because it's not in a guild",
                message.id,
            )

        text = preprocessing.process(message.clean_content)

        if not text:
            return logger.debug(
                "Ignoring message %s because it's empty after processing",
                message.id,
            )

        embedding = await self.vectorizer.aencode(text)
        sentiment = calculate_sentiment(text)
        tokens = tokenize_sentence(text)

        key = await messages.save_message(
            self.bot.redis,
            MessageAnalysis(
                user_id=str(message.author.id),
                message_id=str(message.id),
                channel_id=str(message.channel.id),
                guild_id=str(message.guild.id),
                timestamp=message.created_at,
                embedding=embedding,
                sentiment=sentiment,
                tokens=word_frequency(tokens),
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
