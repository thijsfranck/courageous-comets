import datetime
from typing import Annotated

import pydantic
from pydantic import AliasChoices, Field, PlainSerializer

UnixTimestamp = Annotated[
    datetime.datetime,
    PlainSerializer(lambda t: t.timestamp(), return_type=float),
]


class BaseModel(pydantic.BaseModel):
    """Base for model definitions."""

    # Redis tags need to be strings, thus, coerce integers passed during creation to string
    model_config = pydantic.ConfigDict(
        extra="ignore",
        coerce_numbers_to_str=True,
        from_attributes=True,
    )

    def __hash__(
        self,
    ) -> int:  # make hashable BaseModel subclass for async_lru.alru_cache decorator
        return hash((type(self), *tuple(self.__dict__.values())))


class Message(BaseModel):
    """
    Redis model of a Discord message.

    Attributes
    ----------
    message_id : str
        The ID of the message.
    channel_id : str
        The ID of the channel the message was sent in.
    guild_id : str
        The ID of the guild the message was sent in.
    timestamp : UnixTimestamp
        The timestamp when the message was sent.
    user_id : str
        The ID of the user who sent the message.
    """

    message_id: str
    channel_id: str
    guild_id: str
    timestamp: UnixTimestamp
    user_id: str


class SentimentResult(BaseModel):
    """
    Result of sentiment analysis.

    Attributes
    ----------
    neg : float
        The negative sentiment score.
    neu : float
        The neutral sentiment score.
    pos : float
        The positive sentiment score.
    compound : float
        The compound sentiment score.
    """

    neg: float = Field(
        ...,
        serialization_alias="sentiment_neg",
        validation_alias=AliasChoices("neg", "sentiment_neg"),
    )
    neu: float = Field(
        ...,
        serialization_alias="sentiment_neu",
        validation_alias=AliasChoices("neu", "sentiment_neu"),
    )
    pos: float = Field(
        ...,
        serialization_alias="sentiment_pos",
        validation_alias=AliasChoices("pos", "sentiment_pos"),
    )
    compound: float = Field(
        ...,
        serialization_alias="sentiment_compound",
        validation_alias=AliasChoices("compound", "sentiment_compound"),
    )


class MessageAnalysis(Message):
    """
    Analysis of a discord message.

    Attributes
    ----------
    sentiment: courageous_comets.models.SentimentResult
        The result of sentiment analysis on the message.
    tokens: dict[str, int]
        Mapping of token to number of times it appears in message.
    embedding : bytes
        The embedding vector of the content.
    """

    sentiment: SentimentResult
    tokens: dict[str, int]
    embedding: bytes


class MessageFrequency(BaseModel):
    """Number of messages sent over a duration.

    Attributes
    ----------
    timestamp: UnixTimestamp
        The timestamp when the messages were sent.
    nb_messages: int
        The number of messages sent at `timestamp`
    """

    timestamp: UnixTimestamp
    num_messages: int
