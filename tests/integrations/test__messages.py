import discord
import pytest
from pytest_mock import MockerFixture
from redis.asyncio import Redis

from courageous_comets.client import CourageousCometsBot
from courageous_comets.cogs.messages import Messages
from courageous_comets.redis.keys import key_schema


@pytest.fixture()
def cog(bot: CourageousCometsBot) -> Messages:
    """Return an instance of the Messages cog."""
    return Messages(bot)


async def test__messages_on_message__message_saved_to_redis(
    cog: Messages,
    redis: Redis,
    mocker: MockerFixture,
) -> None:
    """
    Test whether messages received by the cog are saved to Redis.

    Asserts
    -------
    - The message key is present in Redis.
    """
    message = mocker.MagicMock(spec=discord.Message)

    message.clean_content = "The quick brown fox jumps over the lazy dog."
    message.id = 1
    message.author.id = 1
    message.author.bot = False
    message.channel.id = 1
    message.guild.id = 1

    await cog.on_message(message)

    key = key_schema.guild_messages(guild_id=1, message_id=1)
    key_exists = await redis.exists(key)

    assert key_exists
