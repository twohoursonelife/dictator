import random
import re
from datetime import timedelta
from itertools import batched

import discord
from db_manager import db_connection as db_conn
from exceptions import (
    UserAlreadyRegisteredError,
    UsernameAlreadyExistsError,
    UsernameValidationError,
)


def get_user_by_discord_id(discord_id: int):
    with db_conn() as db:
        db.execute(
            "SELECT email, login_key FROM ticketServer_tickets WHERE discord_id = %s LIMIT 1",
            (discord_id,),
        )
        return db.fetchone()


def get_user_by_username(username: str):
    with db_conn() as db:
        db.execute(
            "SELECT email FROM ticketServer_tickets WHERE email = %s LIMIT 1",
            (username,),
        )
        return db.fetchone()


def is_valid_username(username: str) -> None:
    """
    Validates a username is within our parameters.
    This validation loosely follows Discord's username rules.
    """

    # Whitelist pattern (^ negates).
    # Any character not specified is invalid.
    if re.search("[^a-zA-Z0-9-]", username):
        raise UsernameValidationError(
            "Usernames can only contain upper and lower latin letters (a-z) as well as 0-9 and - (hyphen)."
        )

    if not (3 <= len(username) <= 32):
        raise UsernameValidationError(
            "Usernames must be 3 or more chracters and 32 or less characters in length."
        )


def is_user_already_registered(discord_id: int) -> None:
    if get_user_by_discord_id(discord_id):
        raise UserAlreadyRegisteredError()


def is_unique_username(username: str) -> None:
    if get_user_by_username(username):
        raise UsernameAlreadyExistsError()


def generate_login_key() -> str:
    """
    Generates a login_key.
    This is used like a password and is equivalent to a game activation code.

    Consists of 20 random characters, split into 4 chunks of 5 each seperated by a hyphen.
    e.g. F93V7-GVD69-UERJF-7WTTE
    """
    readable_characters = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"
    raw_key = random.choices(readable_characters, k=20)
    chunks = ["".join(chunk) for chunk in batched(raw_key, 5)]
    return "-".join(chunks)


def is_new_discord_user(discord_user: discord.User) -> bool:
    new_point = discord.utils.utcnow() - timedelta(weeks=1)

    # If created after (greater than) new_point, they're wihtin the new period
    return discord_user.created_at > new_point
