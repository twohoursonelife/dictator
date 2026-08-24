from collections.abc import Callable
from typing import TypeVar

from discord import app_commands

from dictator.settings import config

T = TypeVar("T")


def admin_only() -> Callable[[T], T]:
    """Make an application command guild-only and available to administrators.

    Discord uses the default permissions to hide the command from members who do
    not have its Administrator permission. The role check remains the authoritative
    runtime check, so the configured administrator role is still required.
    """

    def decorator(command: T) -> T:
        command = app_commands.guild_only()(command)
        command = app_commands.default_permissions(administrator=True)(command)
        command = app_commands.checks.has_role(config.ADMIN_ROLE_ID)(command)
        return command

    return decorator
