from enum import StrEnum


class StatisticScope(StrEnum):
    """Scope of statistics results to fetch."""

    GUILD = "guild_id"
    CHANNEL = "channel_id"
    USER = "user_id"
