from enum import IntEnum, StrEnum


class StatisticScope(StrEnum):
    """Scope of statistics results to fetch."""

    GUILD = "guild_id"
    CHANNEL = "channel_id"
    USER = "user_id"


class Duration(IntEnum):
    """Number of seconds in time durations."""

    minute = 60
    hourly = 60 * 60
    daily = 60 * 60 * 24
