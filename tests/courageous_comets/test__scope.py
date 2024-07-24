import pytest

from courageous_comets.enums import StatisticScope
from courageous_comets.redis.messages import build_search_scope


@pytest.mark.parametrize(
    ("guild_id", "ids", "scope", "expected"),
    [
        ("1", ["2", "3"], StatisticScope.GUILD, "@guild_id:{1}"),
        ("1", None, StatisticScope.GUILD, "@guild_id:{1}"),
        ("1", ["2", "3"], StatisticScope.CHANNEL, "(@guild_id:{1} @channel_id:{2|3})"),
        ("1", ["2", "3"], StatisticScope.USER, "(@guild_id:{1} @user_id:{2|3})"),
    ],
)
def test__build_search_scope(
    guild_id: str,
    ids: list[str] | None,
    scope: StatisticScope,
    expected: str,
) -> None:
    """Tests whether the correct search scope is generated."""
    assert str(build_search_scope(guild_id, ids, scope)) == expected
