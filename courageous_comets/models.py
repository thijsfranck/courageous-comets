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
    """Redis model of a Discord message."""

    message_id: str
    channel_id: str
    guild_id: str
    timestamp: UnixTimestamp
    user_id: str
    content: str
    embedding: bytes


class SentimentResult(BaseModel):
    """Result of sentiment analysis."""

    neg: float
    neu: float
    pos: float
    compound: float
