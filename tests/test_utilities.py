from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from typing import cast

import discord

from dictator.utilities import (
    is_discord_account_old_enough,
    sanitise_username,
)


def test_sanitise_username():
    assert sanitise_username("normalname") == "normalname"
    assert sanitise_username("name_with_underscore") == "name-with-underscore"
    assert sanitise_username("name.with.dot") == "name-with-dot"
    assert sanitise_username("invalid!@#chars") == "invalidchars"
    assert sanitise_username("mixed_.name!123") == "mixed--name123"
    assert sanitise_username("a" * 40) == "a" * 32
    assert sanitise_username("_.!@#") == "--"


def test_discord_account_age_disabled():
    user = cast(discord.User, SimpleNamespace(created_at=datetime.now(UTC)))

    assert is_discord_account_old_enough(user, 0)


def test_discord_account_age_restriction():
    now = datetime.now(UTC)
    old_user = cast(discord.User, SimpleNamespace(created_at=now - timedelta(days=8)))
    new_user = cast(discord.User, SimpleNamespace(created_at=now - timedelta(days=6)))

    assert is_discord_account_old_enough(old_user, 7)
    assert not is_discord_account_old_enough(new_user, 7)
