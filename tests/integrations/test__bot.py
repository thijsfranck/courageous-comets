import discord
from pytest_mock import MockerFixture
from redis.asyncio import Redis

from courageous_comets.client import CourageousCometsBot
from courageous_comets.redis.keys import key_schema


async def test__save_message(bot: CourageousCometsBot, redis: Redis, mocker: MockerFixture) -> None:
    """
    Test whether messages received by the bot are saved to Redis.

    Asserts
    -------
    - The message is saved to Redis.
    """
    message = mocker.MagicMock(spec=discord.Message)

    message.content = "The quick brown fox jumps over the lazy dog."
    message.id = 1
    message.author.id = 1
    message.channel.id = 1
    message.guild.id = 1

    await bot.save_message(message)

    key = key_schema.guild_messages(1)
    key_exists = await redis.exists(key)

    assert key_exists
