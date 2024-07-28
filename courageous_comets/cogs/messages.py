import logging

import discord
from discord.ext import commands

from courageous_comets.client import CourageousCometsBot
from courageous_comets.processing import process_message

logger = logging.getLogger(__name__)


class Messages(commands.Cog):
    """
    A cog that listens for messages from discord and forwards them to processing.

    Attributes
    ----------
    bot : CourageousCometsBot
        The bot instance.
    """

    def __init__(self, bot: CourageousCometsBot) -> None:
        self.bot = bot

    @commands.Cog.listener(name="on_message")
    async def on_message(self, message: discord.Message) -> None:
        """
        When a message is received, forward it to processing.

        Ignore messages that are not in a guild or if the bot is not connected to Redis.

        Parameters
        ----------
        message : discord.Message
            The message to save.
        """
        if not self.bot.redis:
            return logger.error(
                "Ignoring message %s because the bot is not connected to Redis",
                message.id,
            )

        validation_errors = {
            "bot": message.author.bot,
            "empty": not message.clean_content,
            "sync": self.bot.user in message.mentions and "sync" in message.clean_content,
        }

        if any(validation_errors.values()):
            return logger.debug(
                "Ignoring message %s, reason: %s",
                message.id,
                validation_errors,
            )

        key = await process_message(
            message,
            redis=self.bot.redis,
            vectorizer=self.bot.vectorizer,
        )

        return logger.debug(
            "Processed message %s, saved with key %s",
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
