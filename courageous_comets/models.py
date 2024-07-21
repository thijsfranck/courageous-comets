import datetime
from typing import Annotated

import pydantic
from pydantic import PlainSerializer

UnixTimestamp = Annotated[
    datetime.datetime,
    PlainSerializer(lambda t: t.timestamp(), return_type=float),
]


class BaseModel(pydantic.BaseModel):
    """Base for model definitions."""

    # Redis tags need to be strings, thus, coerce integers passed during creation to string
    model_config = pydantic.ConfigDict(extra="ignore", coerce_numbers_to_str=True)


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
    content : str
        The content of the message.
    embedding : bytes
        The embedding of the message.
    """

    message_id: str
    channel_id: str
    guild_id: str
    timestamp: UnixTimestamp
    user_id: str
    content: str
    embedding: bytes


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

    neg: float
    neu: float
    pos: float
    compound: float