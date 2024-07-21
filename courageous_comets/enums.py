import enum


class StatisticScopeEnum(enum.Enum):
    """Scope of statistics results to fetch."""

    GUILD = enum.auto()
    CHANNEL = enum.auto()
    USER = enum.auto()
