from redis.asyncio import Redis
from redisvl.index import AsyncSearchIndex
from redisvl.query import VectorQuery
from redisvl.query.filter import Tag

from courageous_comets import models
from courageous_comets.enums import StatisticScopeEnum
from courageous_comets.redis import schema
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


async def save_message(
    redis: Redis,
    message: models.VectorizedMessage,
) -> str:
    """Save a message on Redis.

    Parameters
    ----------
    redis : Redis
        The Redis connection instance.
    message : models.VectorizedMessage
        The message to save

    Returns
    -------
    str
        The key to the data on Redis.
    """
    index = AsyncSearchIndex.from_dict(schema.MESSAGE_SCHEMA)
    index.set_client(redis)
    return (
        await index.load(
            [message.model_dump()],
            keys=[
                key_schema.guild_messages(
                    guild_id=message.guild_id,
                    message_id=message.message_id,
                ),
            ],
        )
    )[0]


async def get_similar_messages(
    redis: Redis,
    message: models.Message,
    embedding: bytes,
    limit: int = 10,
    scope: StatisticScopeEnum = StatisticScopeEnum.GUILD,
) -> list[models.Message]:
    """
    Get the messages with similar semantics to the provided message.

    Parameters
    ----------
    redis : Redis
        The Redis connection instance.
    message : models.Message
        The comparison message.
    embedding: bytes
        The vector embedding of the message.
    limit   :
        The number of similar messages to fetch.
    scope   : enums.StatisticScopeEnum
        The scope to limit the search.

    Returns
    -------
    list[models.Message]
        The messages that are similar semantically.
    """
    index = AsyncSearchIndex.from_dict(schema.MESSAGE_SCHEMA)
    index.set_client(redis)
    # Determine the scope to filter the search
    match scope:
        case StatisticScopeEnum.GUILD:
            filter_expression = Tag("guild_id") == message.guild_id
        case StatisticScopeEnum.CHANNEL:
            filter_expression = Tag("channel_id") == message.channel_id
        case StatisticScopeEnum.USER:
            filter_expression = Tag("user_id") == message.user_id
        case _:
            error_message = f"Unhandled scope: {scope!r}"
            raise ValueError(error_message)

    query = VectorQuery(
        vector=embedding,
        vector_field_name="embedding",
        return_fields=[
            "message_id",
            "channel_id",
            "user_id",
            "content",
            "guild_id",
            "timestamp",
        ],
        filter_expression=filter_expression,
        num_results=limit,
    )
    results = await index.query(query)
    return [models.Message.model_validate(result) for result in results]
