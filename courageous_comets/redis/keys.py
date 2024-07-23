from collections.abc import Callable
from functools import wraps
from typing import ParamSpec

from courageous_comets import settings

P = ParamSpec("P")
Prefixable = Callable[P, str]


def prefix_key(func: Prefixable[P]) -> Prefixable[P]:
    """
    Prefix the key returned by the decorated function with the Redis key prefix.

    This function is intended to be used as a decorator.

    Parameters
    ----------
    func : courageous_comets.redis.keys.Prefixable[P]
        The function to decorate.

    Returns
    -------
    courageous_comets.redis.keys.Prefixable[P]
        The decorated function.
    """

    @wraps(func)
    def prefixed_method(*args: P.args, **kwargs: P.kwargs) -> str:
        key = func(*args, **kwargs)
        return f"{settings.REDIS_KEYS_PREFIX}:{key}"

    return prefixed_method


class KeySchema:
    """
    A class to generate key names for Redis data structures.

    This class contains a reference to all possible key names used
    by the application.
    """

    @prefix_key
    def guild_messages(self, *, guild_id: int, message_id: int) -> str:
        """Key to messages for a Discord guild.

        Redis type: hash
        """
        return f"messages:{guild_id}:{message_id}"

    @prefix_key
    def guild_message_tokens(self, guild_id: int) -> str:
        """Key to message tokens for a Discord guild.

        Redis type: hash
        """
        return f"messages:tokens:{guild_id}"


key_schema = KeySchema()
