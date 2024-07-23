from redis.asyncio import Redis
from redisvl.index import AsyncSearchIndex
from redisvl.query import FilterQuery, VectorQuery
from redisvl.query.filter import FilterExpression, Num, Tag

from courageous_comets import models, settings
from courageous_comets.enums import StatisticScopeEnum
from courageous_comets.redis import schema
from courageous_comets.redis.keys import key_schema


def get_search_scope(
    scope: StatisticScopeEnum,
    message: models.Message,
) -> FilterExpression:
    """Determine the scope of a search.

    Parameters
    ----------
    scope : courageous_comets.enums.StatisticScopeEnum
        The scope of a search.
    message : courageous_comets.models.Message
        The comparison message.

    Returns
    -------
    redisvl.query.FilterExpression
        The redis filter expression for the specified scope

    """
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
    return filter_expression


async def update_message_tokens(
    redis: Redis,
    guild_id: int,
    words: dict[str, int],
) -> dict[str, int]:
    """
    Update the word frequencies for a guild's messages in the database.

    Parameters
    ----------
    redis : redis.Redis
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
    sentiment: models.SentimentResult,
) -> str:
    """Save a message on Redis.

    Parameters
    ----------
    redis : redis.Redis
        The Redis connection instance.
    message : courageous_comets.models.VectorizedMessage
        The message to save
    sentiment: courageous_comets.models.SentimentResult
        The sentiment analayis result of the message

    Returns
    -------
    str
        The key to the data on Redis.
    """
    index = AsyncSearchIndex.from_dict(schema.MESSAGE_SCHEMA)
    index.set_client(redis)
    return (
        await index.load(
            [{**message.model_dump(), **sentiment.model_dump(by_alias=True)}],
            keys=[
                key_schema.guild_messages(
                    guild_id=message.guild_id,
                    message_id=message.message_id,
                ),
            ],
        )
    )[0]


async def get_messages_by_semantics_similarity(
    redis: Redis,
    message: models.Message,
    embedding: bytes,
    limit: int = settings.QUERY_LIMIT,
    scope: StatisticScopeEnum = StatisticScopeEnum.GUILD,
) -> list[models.Message]:
    """
    Get the messages with similar semantics to the provided message.

    Parameters
    ----------
    redis : redis.Redis
        The Redis connection instance.
    message : courageous_comets.models.Message
        The comparison message.
    embedding: bytes
        The vector embedding of the message.
    limit : int
        The number of similar messages to fetch (default: settings.PAGE_SIZE).
    scope : courageous_comets.enums.StatisticScopeEnum
        The scope to limit the search (default: enums.StatisticScopeEnum.GUILD).

    Returns
    -------
    list[courageous_comets.models.Message]
        The messages that are semantically similar
    """
    index = AsyncSearchIndex.from_dict(schema.MESSAGE_SCHEMA)
    index.set_client(redis)
    # Determine the scope to filter the search
    search_scope = get_search_scope(scope, message)
    query = VectorQuery(
        vector=embedding,
        vector_field_name="embedding",
        return_fields=[
            "message_id",
            "channel_id",
            "user_id",
            "guild_id",
            "timestamp",
        ],
        filter_expression=search_scope,
        num_results=limit,
    )
    results = await index.query(query)
    return [models.Message.model_validate(result) for result in results]


async def get_messages_by_sentiment_similarity(  # noqa: PLR0913
    redis: Redis,
    message: models.Message,
    sentiment: models.SentimentResult,
    radius: float,
    limit: int = settings.QUERY_LIMIT,
    scope: StatisticScopeEnum = StatisticScopeEnum.GUILD,
) -> list[models.Message]:
    """
    Get the messages with similar sentiment analysis.

    Parameters
    ----------
    redis : redis.Redis
        The Redis connection instance.
    sentiment : courageous_comets.models.SentimentResult
        The sentiment analayis result of a message.
    radius: float
        The distance threshold of the search.
    limit : int
        The number of similar messages to fetch (default: settings.PAGE_SIZE).
    scope : courageous_comets.enums.StatisticScopeEnum
        The scope to limit the search (default: enums.StatisticScopeEnum.GUILD).

    Returns
    -------
    list[courageous_comets.models.Message]
        The messages that are sentimentally similar.
    """
    index = AsyncSearchIndex.from_dict(schema.MESSAGE_SCHEMA)
    index.set_client(redis)
    # Determine the scope to filter the search
    search_scope = get_search_scope(scope, message)
    low = Num("sentiment_compound") >= sentiment.compound  # pyright: ignore
    high = Num("sentiment_compound") <= sentiment.compound + radius  # pyright: ignore
    filter_expression = search_scope & low & high
    query = FilterQuery(
        return_fields=["message_id", "user_id", "channel_id", "guild_id", "timestamp"],
        filter_expression=filter_expression,
        num_results=limit,
    )
    results = await index.query(query)
    return [models.Message.model_validate(result) for result in results]
