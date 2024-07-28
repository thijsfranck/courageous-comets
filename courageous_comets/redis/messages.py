import datetime
import itertools
import json
import logging
from collections import Counter

import redis.commands.search.aggregation as aggregations
from redis.asyncio import Redis
from redis.commands.search import AsyncSearch, reducers
from redisvl.index import AsyncSearchIndex
from redisvl.query import FilterQuery, VectorQuery
from redisvl.query.filter import FilterExpression, Num, Tag
from redisvl.query.query import BaseQuery

from courageous_comets import models, settings
from courageous_comets.enums import Duration, StatisticScope
from courageous_comets.redis import schema
from courageous_comets.redis.keys import key_schema

logger = logging.getLogger(__name__)

# List of courageous_comets.models.Message return fields used acrosss queries
# that return a list of courageous_comets.models.Message
RETURN_FIELDS = ["message_id", "user_id", "channel_id", "guild_id", "timestamp"]


def _get_raw_index(redis: Redis) -> AsyncSearch:
    """Get the raw messages index on Redis."""
    index = AsyncSearchIndex.from_dict(schema.MESSAGE_SCHEMA)
    return redis.ft(index.schema.index.name)


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

    return [models.Message.model_validate(doc) for doc in results.docs if results.total]


def build_search_scope(
    guild_id: str,
    ids: list[str] | None,
    scope: StatisticScope,
) -> FilterExpression:
    """
    Build a filter expression based on the given id and specified scope.

    Parameters
    ----------
    guild_id: str
        The ID of the guild to make the search.
    ids : list[str] | None
        The additional IDs to limit the search to.
    scope : courageous_comets.enums.StatisticScope
        The scope of the additional IDs.

    Notes
    -----
    If the scope of the search is courageous_comets.enums.StatisticScope.GUILD,
        the `ids` are ignored.

    Returns
    -------
    redisvl.query.FilterExpression
        The redis filter expression for the specified scope.
    """
    search_scope = Tag(StatisticScope.GUILD) == guild_id

    # Ignore the other IDs as this would imply searching across multiple scopes.
    if scope == StatisticScope.GUILD or not ids:
        return search_scope

    return search_scope & (Tag(scope) == ids)


async def save_message(
    redis: Redis,
    message: models.MessageAnalysis,
) -> str:
    """Save a message on Redis.

    Parameters
    ----------
    redis : redis.Redis
        The Redis connection instance.
    message : courageous_comets.models.MessageAnalysis
        The message to save.

    Returns
    -------
    str
        The key to the data on Redis.
    """
    payload = {
        "message_id": message.message_id,
        "channel_id": message.channel_id,
        "guild_id": message.guild_id,
        "timestamp": message.timestamp.timestamp(),
        "user_id": message.user_id,
        "sentiment_neg": message.sentiment.neg,
        "sentiment_neu": message.sentiment.neu,
        "sentiment_pos": message.sentiment.pos,
        "sentiment_compound": message.sentiment.compound,
        "embedding": message.embedding,
        "tokens": json.dumps(message.tokens),
    }
    key = key_schema.guild_messages(
        guild_id=int(message.guild_id),
        message_id=int(message.message_id),
    )
    await redis.hset(key, mapping=payload)  # type: ignore
    return key


async def get_message_sentiment(
    key: str,
    *,
    redis: Redis,
) -> models.SentimentResult | None:
    """
    Get the sentiment of message from the database given its key.

    Parameters
    ----------
    key: str
        The key of the message to fetch.
    redis : redis.Redis
        The Redis connection instance.

    Returns
    -------
    courageous_comets.models.SentimentResult | None
        The sentiment analysis result if found, else None.
    """
    fields = ["sentiment_neg", "sentiment_neu", "sentiment_pos", "sentiment_compound"]

    if not redis.exists(key):
        return None

    data = await redis.hmget(key, fields)  # type: ignore

    has_all_fields = len(data) == len(fields)
    any_none = any(value is None for value in data)

    if not has_all_fields or any_none:
        logger.warning("Missing sentiment analysis data for message %s.", key)
        return None

    return models.SentimentResult.model_validate(
        {key: float(value) for key, value in zip(fields, data, strict=True)},
    )


async def get_recent_messages(
    redis: Redis,
    *,
    guild_id: str,
    ids: list[str] | None = None,
    scope: StatisticScope = StatisticScope.CHANNEL,
    limit: int = settings.QUERY_LIMIT,
) -> list[models.Message]:
    """
    Get the most recent `limit` messages.

    Parameters
    ----------
    redis : redis.Redis
        The Redis connection instance.
    guild_id: str
        The ID of the guild to make the search.
    ids : list[str]
        Optional list of IDs to search for.
    scope : courageous_comets.enums.StatisticScope
        The scope of additional IDs (default: courageous_comets.enums.StatisticScope.CHANNEL).
        Ignored it is equal to courageous_comets.enums.StatisticScope.GUILD,
    limit : int
        The number of messages to fetch (default: courageous_comets.settings.QUERY_LIMIT).

    Returns
    -------
    list[courageous_comets.models.Message]
        The list of recent messages.
    """
    search_scope = build_search_scope(guild_id, ids, scope)

    query = FilterQuery(
        return_fields=RETURN_FIELDS,
        filter_expression=search_scope,
        num_results=limit,
    )

    return await _get_messages_from_query(redis, query)


async def get_messages_by_semantics_similarity(  # noqa: PLR0913
    redis: Redis,
    *,
    guild_id: str,
    embedding: bytes,
    ids: list[str] | None = None,
    scope: StatisticScope = StatisticScope.CHANNEL,
    limit: int = settings.QUERY_LIMIT,
) -> list[models.Message]:
    """
    Get the messages with similar semantics to the provided message.

    Parameters
    ----------
    redis : redis.Redis
        The Redis connection instance.
    guild_id: str
        The ID of the guild to make the search.
    embedding: bytes
        The vector embedding of the message.
    ids : list[str] | None
        Optional list of IDs to search for.
    scope : courageous_comets.enums.StatisticScope
        The scope of additional IDs (default: courageous_comets.enums.StatisticScopeEnum.CHANNEL).
        Ignored if it is set to courageous_comets.enums.StatisticScope.GUILD.
    limit : int
        The number of similar messages to fetch (default: courageous_comets.settings.QUERY_LIMIT).

    Returns
    -------
    list[courageous_comets.models.Message]
        The messages that are semantically similar
    """
    search_scope = build_search_scope(guild_id, ids, scope)

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
    *,
    guild_id: str,
    sentiment: float,
    radius: float,
    ids: list[str] | None = None,
    scope: StatisticScope = StatisticScope.CHANNEL,
    limit: int = settings.QUERY_LIMIT,
) -> list[models.Message]:
    """
    Get the messages with similar sentiment analysis.

    Parameters
    ----------
    redis : redis.Redis
        The Redis connection instance.
    guild_id: str
        The ID of the guild to make the search.
    sentiment : float
        The sentiment analayis result of message.
    radius: float
        The distance threshold of the search.
    ids : list[str] | None
        Optional list of IDs to search for.
    scope : courageous_comets.enums.StatisticScope
        The scope of additional IDs (default: courageous_comets.enums.StatisticScopeEnum.CHANNEL).
        Ignored if it is set to courageous_comets.enums.StatisticScope.GUILD.
    limit : int
        The number of similar messages to fetch (default: settings.PAGE_SIZE).

    Returns
    -------
    list[courageous_comets.models.Message]
        The messages that are sentimentally similar.
    """
    search_scope = build_search_scope(guild_id, ids, scope)

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


async def get_tokens_count(
    redis: Redis,
    *,
    guild_id: str,
    ids: list[str] | None = None,
    scope: StatisticScope = StatisticScope.CHANNEL,
    limit: int = settings.QUERY_LIMIT,
) -> Counter[str]:
    """
    Get the count of tokens across messages.

    Parameters
    ----------
    redis: redis.Redis
        The Redis connection instance.
    guild_id: str
        The ID of the guild to make the search
    ids: list[strr]
        Optional list of IDs to search for.
    scope : courageous_comets.enums.StatisticScope
        The scope of additional IDs (default: courageous_comets.enums.StatisticScope.CHANNEL).
        Ignored it is equal to courageous_comets.enums.StatisticScope.GUILD,
    limit : int
        The number of messages to fetch (default: courageous_comets.settings.QUERY_LIMIT).

    Returns
    -------
    collections.Counter
        Mapping of each token to its count.
    """
    search_scope = build_search_scope(guild_id, ids, scope)
    index = AsyncSearchIndex.from_dict(schema.MESSAGE_SCHEMA)
    index.set_client(redis)

    query = FilterQuery(
        return_fields=["tokens"],
        filter_expression=search_scope,
        num_results=limit,
    )

    results = await index.search(
        query.query.sort_by("timestamp", asc=False),
        query.params,
    )

    counter = Counter()
    tokens: list[dict[str, int]] = [json.loads(doc.tokens) for doc in results.docs if results.total]

    for token in tokens:
        counter.update(token)

    return counter


def _calculate_duration_range(duration: Duration) -> tuple[float, float]:
    """Calculate the lower and upper bounds of a duration.

    Parameters
    ----------
    duration: courageous_comets.enums.Duration
        The duration to be used for aggregation.

    Returns
    -------
    tuple[float, float]
        The lower and upper bounds of the duration as UNIX timestamps.
    """
    upper = datetime.datetime.now(datetime.UTC)
    match duration:
        case Duration.minute:
            lower = upper - datetime.timedelta(minutes=60)
        case Duration.hourly:
            lower = upper - datetime.timedelta(hours=24)
        case Duration.daily:
            lower = upper - datetime.timedelta(days=7)
        case _:
            error_message = f"Unhandled duration: {duration}"
            raise ValueError(error_message)

    return (lower.timestamp(), upper.timestamp())


async def get_messages_frequency(  # noqa: PLR0913
    redis: Redis,
    *,
    guild_id: str,
    ids: list[str] | None = None,
    scope: StatisticScope = StatisticScope.CHANNEL,
    limit: int = settings.QUERY_LIMIT,
    duration: Duration = Duration.hourly,
) -> list[models.MessageFrequency]:
    """
    Get the rate of messages over an interval.

    Parameters
    ----------
    redis : Redis
        The Redis connection instance.
    guild_id : str
        The ID of the guild to make the search.
    ids : list[str], optional
        Optional list of IDs to search for. Defaults to None.
    scope : StatisticScope, optional
        The scope of additional IDs (default: StatisticScope.CHANNEL).
        Ignored if it is equal to StatisticScope.GUILD.
    duration : Duration, optional
        The duration over which to make the aggregation (default: Duration.HOUR).
    limit : int, optional
        The number of messages to aggregate over (default: settings.QUERY_LIMIT).

    Returns
    -------
    list[models.MessageFrequency]
        A list of message frequency at different timestamps.
    """
    search_scope = build_search_scope(guild_id, ids, scope)
    lower_timestamp, upper_timestamp = _calculate_duration_range(duration)
    filter_expression = (
        search_scope
        & (Num("timestamp") >= lower_timestamp)  # type: ignore
        & (Num("timestamp") <= upper_timestamp)  # type: ignore
    )
    index = _get_raw_index(redis)

    # Define a reducer to count distinct message IDs and alias the result as "num_messages"
    reducer = reducers.count_distinct("@message_id").alias("num_messages")

    # Build the aggregation query
    query = (
        aggregations.AggregateRequest(str(filter_expression))
        .limit(
            0,
            limit,
        )
        # Create a new property `timestamp` rounded to the start of the interval
        .apply(
            timestamp=f"floor(@timestamp) - (floor(@timestamp) % {duration.value})",
        )
        # Group results by interval using the new `timestamp` property
        .group_by(["@timestamp"], reducer)
        # Sort results by the timestamp and return at most 60 entries. We never
        # get more than 60 groups because the smallest time division is 60
        # minutes according to our duration values.
        .sort_by(aggregations.Asc("@timestamp"), max=60)  # type: ignore
    )

    # Execute the aggregation query on the index
    results = await index.aggregate(query)  # type: ignore

    # Deserialize all rows as dictionaries. Each row is a flat list of key-value pairs.
    return [
        models.MessageFrequency.model_validate_strings(dict(itertools.batched(row, 2)))
        for row in results.rows
    ]


async def get_average_sentiment(
    redis: Redis,
    *,
    guild_id: str,
    ids: list[str] | None = None,
    scope: StatisticScope = StatisticScope.CHANNEL,
    limit: int = settings.QUERY_LIMIT,
) -> list[models.SentimentResult]:
    """
    Get the average sentiment of messages for the given ids and scope.

    Parameters
    ----------
    redis : Redis
        The Redis connection instance.
    guild_id : str
        The ID of the guild to make the search.
    ids : list[str], optional
        Optional list of IDs to search for. Defaults to None.
    scope : StatisticScope, optional
        The scope of additional IDs (default: StatisticScope.CHANNEL).
        Ignored if it is equal to StatisticScope.GUILD.
    limit : int, optional
        The number of messages to aggregate over (default: settings.QUERY_LIMIT).
    """
    search_scope = build_search_scope(guild_id, ids, scope)
    index = _get_raw_index(redis)

    # Define reducers to calculate the average scores for each sentiment type
    avg_sentiment = reducers.avg("@sentiment_compound").alias("sentiment_compound")
    avg_negativity = reducers.avg("@sentiment_neg").alias("sentiment_neg")
    avg_neutrality = reducers.avg("@sentiment_neu").alias("sentiment_neu")
    avg_positivity = reducers.avg("@sentiment_pos").alias("sentiment_pos")

    # Build the aggregation query
    query = (
        aggregations.AggregateRequest(f"{search_scope!s}")
        .limit(0, limit)
        .group_by(
            [f"@{scope}"],
            avg_sentiment,
            avg_negativity,
            avg_neutrality,
            avg_positivity,
        )
    )

    # Execute the aggregation query on the index
    results = await index.aggregate(query)  # type: ignore

    # Deserialize all rows as dictionaries. Each row is a flat list of key-value pairs.
    return [
        models.SentimentResult.model_validate(
            {
                key: float(value)
                for row in results.rows
                for key, value in itertools.batched(row, 2)
                if value is not None
            },
        ),
    ]
