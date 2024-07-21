from redis.asyncio import Redis

from courageous_comets.redis.keys import key_schema


async def update_message_tokens(
    redis: Redis,
    guild_id: int,
    words: dict[str, int],
) -> dict[str, int]:
    """
    Update the word frequencies for a guild's messages in the database.

    Parameters
    ----------
    redis : Redis
        The Redis connection instance.
    guild_id : int
        The ID of the guild.
    words : dict[str, int]
        The words and their frequencies to update.

    Returns
    -------
    dict[str, int]
        The updated word frequencies.
    """
    async with redis.pipeline() as pipe:
        # Queue the increment operations for each word
        for word, frequency in words.items():
            pipe.hincrby(key_schema.guild_message_tokens(guild_id), word, frequency)

        # Execute the pipeline
        new_frequencies: list[int] = await pipe.execute()

    # Given dictionary keys are iterated in insertion order, execution of the
    # instructions are evaluated in the same order, thus, the return values are
    # in the same order.
    return dict(zip(words.keys(), new_frequencies, strict=False))
