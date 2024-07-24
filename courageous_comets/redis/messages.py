from redis.asyncio import Redis
from redisvl.index import AsyncSearchIndex
from redisvl.query import FilterQuery, VectorQuery
from redisvl.query.filter import FilterExpression, Num, Tag
from redisvl.query.query import BaseQuery

from courageous_comets import models, settings
from courageous_comets.enums import StatisticScope
from courageous_comets.redis import schema
from courageous_comets.redis.keys import key_schema

# List of courageous_comets.models.Message return fields used acrosss queries
# that return a list of courageous_comets.models.Message
RETURN_FIELDS = ["message_id", "user_id", "channel_id", "guild_id", "timestamp"]


async def _get_messages_from_query(
    redis: Redis,
    query: BaseQuery,
) -> list[models.Message]:
    """Get a list of messages from Redis query.

    Assumes the fields returned in the query correspond to the attributes
    of the courageous_comets.models.Message.

    Parameters
    ----------
    redis: redis.Redis
        The Redis connection instance.
    query: redisvl.query.query.BaseQuery
        The query to run on Redis.

    Returns
    -------
    courageous_comets.models.Message
        The list of messages from the query.
    """
    index = AsyncSearchIndex.from_dict(schema.MESSAGE_SCHEMA)
    index.set_client(redis)

    results = await index.search(
        query.query.sort_by("timestamp", asc=False),
        query.params,
    )

    if results.total == 0:
        return []

    return [models.Message.model_validate(doc) for doc in results.docs]


def build_search_scope(
    id_: str,
    scope: StatisticScope,
) -> FilterExpression:
    """
    Build a filter expression based on the given id and specified scope.

    Parameters
    ----------
    id_ : str
        The ID to search for.
    scope : courageous_comets.enums.StatisticScope
        The scope to limit the search.

    Returns
    -------
    redisvl.query.FilterExpression
        The redis filter expression for the specified scope.
    """
    return Tag(scope) == id_


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

    # Merge the message and sentiment data into a single record
    data = {**message.model_dump(), **sentiment.model_dump(by_alias=True)}

    key = key_schema.guild_messages(
        guild_id=int(message.guild_id),
        message_id=int(message.message_id),
    )

    results = await index.load(data=[data], keys=[key])

    return results[0]


async def get_recent_messages(
    redis: Redis,
    id_: str,
    scope: StatisticScope = StatisticScope.GUILD,
    limit: int = settings.QUERY_LIMIT,
) -> list[models.Message]:
    """
    Get the most recent `limit` messages.

    Parameters
    ----------
    redis : redis.Redis
        The Redis connection instance.
    id_ : str
        The ID of the entity to search for. It should correspond to the given scope.
    scope : courageous_comets.enums.StatisticScope
        The scope to limit the search (default: enums.StatisticScopeEnum.GUILD).
    limit : int
        The number of messages to fetch (default: settings.PAGE_SIZE).

    Returns
    -------
    list[courageous_comets.models.Message]
        The list of recent messages.
    """
    search_scope = build_search_scope(id_, scope)

    query = FilterQuery(
        return_fields=RETURN_FIELDS,
        filter_expression=search_scope,
        num_results=limit,
    )

    return await _get_messages_from_query(redis, query)


async def get_messages_by_semantics_similarity(
    redis: Redis,
    id_: str,
    embedding: bytes,
    scope: StatisticScope = StatisticScope.GUILD,
    limit: int = settings.QUERY_LIMIT,
) -> list[models.Message]:
    """
    Get the messages with similar semantics to the provided message.

    Parameters
    ----------
    redis : redis.Redis
        The Redis connection instance.
    id_ : str
        The ID of the entity to search for. It should correspond to the given scope.
    embedding: bytes
        The vector embedding of the message.
    scope : courageous_comets.enums.StatisticScope
        The scope to limit the search (default: enums.StatisticScopeEnum.GUILD).
    limit : int
        The number of similar messages to fetch (default: settings.PAGE_SIZE).

    Returns
    -------
    list[courageous_comets.models.Message]
        The messages that are semantically similar
    """
    search_scope = build_search_scope(id_, scope)

    query = VectorQuery(
        vector=embedding,
        vector_field_name="embedding",
        return_fields=RETURN_FIELDS,
        filter_expression=search_scope,
        num_results=limit,
    )

    return await _get_messages_from_query(redis, query)


async def get_messages_by_sentiment_similarity(  # noqa: PLR0913
    redis: Redis,
    id_: str,
    sentiment: float,
    radius: float,
    scope: StatisticScope = StatisticScope.GUILD,
    limit: int = settings.QUERY_LIMIT,
) -> list[models.Message]:
    """
    Get the messages with similar sentiment analysis.

    Parameters
    ----------
    redis : redis.Redis
        The Redis connection instance.
    id_ : str
        The ID of the entity to search for. It should correspond to the given scope.
    sentiment : float
        The sentiment analayis result of message.
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
    search_scope = build_search_scope(id_, scope)

    # Define lower and upper bounds for the sentiment compound score
    low = Num("sentiment_compound") >= sentiment - radius  # type: ignore
    high = Num("sentiment_compound") <= sentiment + radius  # type: ignore

    filter_expression = search_scope & low & high

    query = FilterQuery(
        return_fields=RETURN_FIELDS,
        filter_expression=filter_expression,
        num_results=limit,
    )

    return await _get_messages_from_query(redis, query)
