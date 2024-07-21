from collections.abc import AsyncGenerator

import discord
import pytest
from pytest_mock import MockerFixture

from courageous_comets.client import CourageousCometsBot
from courageous_comets.redis.keys import key_schema


@pytest.fixture()
async def bot() -> AsyncGenerator[CourageousCometsBot, None]:
    """Fixture that sets up and tears down the CourageousCometsBot instance."""
    instance = CourageousCometsBot()
    await instance.setup_hook()
    yield instance
    await instance.close()


async def test__save_message(bot: CourageousCometsBot, mocker: MockerFixture) -> None:
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

    assert bot.redis is not None
    assert bot.redis.exists(key)
