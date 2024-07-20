from redis.asyncio import Redis

from courageous_comets.redis.keys import key_schema


async def update_message_tokens(
    redis: Redis,
    guild_id: int,
    words: dict[str, int],
) -> dict[str, int]:
    """Update the frequency of each word in a guild."""
    async with redis.pipeline() as pipe:
        for word, frequency in words.items():
            pipe.hincrby(key_schema.guild_message_tokens(guild_id), word, frequency)
        new_frequencies: list[int] = await pipe.execute()
        # Given dictionary keys are iterated in insertion order, execution of the
        # instructions are evaluated in the same order, thus, the return values are
        # in the same order.
        return {  # noqa: C416
            word: frequency for word, frequency in zip(words.keys(), new_frequencies, strict=False)
        }
