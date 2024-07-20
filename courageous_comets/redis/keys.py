from collections.abc import Callable
from functools import wraps
from typing import Any

from courageous_comets import settings


def prefix_key(func: Callable[..., str]) -> Callable[..., str]:
    """Prefix return values of methods with settings.REDIS_KEYS_PREFIX."""

    @wraps(func)
    def prefixed_method(self: object, *args: Any, **kwargs: Any) -> str:  # noqa: ANN401
        key = func(self, *args, **kwargs)
        return f"{settings.REDIS_KEYS_PREFIX}:{key}"

    return prefixed_method


class KeySchema:
    """A class to generate key names for Redis data structures.

    This class contains a reference to all possible key names used
    by the application.
    """

    def __init__(self, prefix: str = settings.REDIS_KEYS_PREFIX) -> None:
        self.prefix = prefix

    @prefix_key
    def guild_messages(self, guild_id: int) -> str:
        """Key to messages for a Discord guild.

        Redis type: hash
        """
        return f"{guild_id}:messages"

    @prefix_key
    def guild_message_tokens(self, guild_id: int) -> str:
        """Key to message tokens for a Discord guild.

        Redis type: hash
        """
        return f"{guild_id}:messages:tokens"

    @prefix_key
    def sentiment_tokens(
        self,
        guild_id: int,
        channel_id: int,
        user_id: int,
        message_id: int,
    ) -> str:
        """
        Key to sentiment tokens for a message.

        Redis type: hash
        """
        return f"{guild_id}:{channel_id}:{user_id}:{message_id}:sentiment"


key_schema = KeySchema()
