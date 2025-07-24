import random
import re
from datetime import timedelta
from hashlib import sha1
from itertools import batched

import discord
from discord.ext import commands

from dictator.constants import ACCOUNT_LOG_CHANNEL_ID
from dictator.db_manager import db_connection as db_conn
from dictator.exceptions import (
    UserAlreadyRegisteredError,
    UsernameAlreadyExistsError,
    UsernameValidationError,
)
from dictator.logger_config import logger


def already_has_role(member: discord.Member, role_name: str) -> bool:
    return discord.utils.get(member.roles, name=role_name) is not None


async def assign_role(
    interaction: discord.Interaction, role_name: str, reason: str
) -> None:
    role_object = discord.utils.get(interaction.guild.roles, name=role_name)
    await interaction.user.add_roles(role_object, reason=reason)


def get_playtime_hours(discord_id: int) -> int:
    """Fetches the total playtime for a user in hours."""
    with db_conn() as db:
        db.execute(
            "SELECT game_total_seconds FROM ticketServer_tickets INNER JOIN reviewServer_user_stats ON reviewServer_user_stats.email = ticketServer_tickets.email WHERE discord_id = %s",
            (discord_id,),
        )
        time_played = db.fetchone()

    if time_played is None:
        return 0

    time_played_hours = time_played[0] // 3600
    return time_played_hours


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


# TODO: more closely follow discords standard
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
    """Raises UserAlreadyRegisteredError if there is already an account associated with the provided discord.User.id."""
    if get_user_by_discord_id(discord_id):
        raise UserAlreadyRegisteredError()


def is_unique_username(username: str) -> None:
    """Raises UsernameAlreadyExistsError if there is already an account with the provided username."""
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


def generate_sha1(input: str) -> str:
    return sha1(input.lower().encode("utf-8")).hexdigest()


##
# TODO: The below commands are higher level than above.
# TODO: Consider somewhere else for them to live.
##


# TODO: refactor to remove bot parameter
async def create_user(
    bot: commands.bot,
    discord_user: discord.User,
    username: str = None,
) -> None:
    """Create a new 2HOL user account."""
    if username is None:
        username = discord_user.name

    # Validation
    try:
        is_user_already_registered(discord_user.id)
        is_valid_username(username)
        is_unique_username(username)

    except UserAlreadyRegisteredError:
        return await send_user_account_details(bot, discord_user)

    except UsernameValidationError as e:
        chosen_username = await prompt_user(
            bot,
            discord_user,
            f"Hey {discord_user.mention}, there was an error when creating your 2HOL account:\n> {str(e)}\n\nPlease reply with a valid username.",
        )

        if chosen_username is None:
            return await discord_user.send(
                "You didn't tell me what to use instead. Use the /account command when you're ready!"
            )

        return await create_user(bot, discord_user, chosen_username)

    except UsernameAlreadyExistsError:
        chosen_username = await prompt_user(
            bot,
            discord_user,
            f"Hey {discord_user.mention}, the username `{username}` is already in use. Please reply with another valid username.",
        )

        if chosen_username is None:
            return await discord_user.send(
                "You didn't tell me what to use instead. Use the /account command when you're ready!"
            )

        return await create_user(bot, discord_user, chosen_username)

    # Creation
    login_key = generate_login_key()

    with db_conn() as db:
        db.execute(
            "INSERT INTO ticketServer_tickets (email, discord_id, login_key) VALUES (%s, %s, %s)",
            (username, discord_user.id, login_key),
        )

    # Notification
    try:
        await discord_user.send(
            f"Welcome to 2HOL {discord_user.mention}!"
            "\n\nPlease know that 2HOL is a moderated community."
            "\nWe ask that you be kind to all players, as you would to a friend."
            "\nAll actions are recorded, please make a [ticket](https://discord.com/channels/423293333864054833/1051420513559392266) in our Discord server if you have a bad experience."
            "\nYou can read more on how to start playing [here](<https://twohoursonelife.com/first-time-playing?ref=create_acc>)."
            "\n\nWhen you're ready, you can use the details below to play the game:"
        )

        await send_user_account_details(bot, discord_user, True)

    # TODO: Extract into generic handler
    except discord.Forbidden:
        notify_user = False

    else:
        notify_user = True

    # Audit
    # TODO: Extract audit log message into generic function
    debug_log_channel = bot.get_channel(ACCOUNT_LOG_CHANNEL_ID)

    embed = discord.Embed(
        title="New game account created", colour=discord.Colour.green()
    )
    embed.add_field(name="Member:", value=f"{discord_user.mention}", inline=True)
    embed.add_field(name="Username:", value=f"{username}", inline=True)
    embed.add_field(
        name="User notification:",
        value="Successful" if notify_user else "Failed",
        inline=True,
    )
    embed.add_field(
        name="User account age:",
        value=(
            "New discord account"
            if is_new_discord_user(discord_user)
            else "Existing discord account"
        ),
        inline=True,
    )
    await debug_log_channel.send(embed=embed)

    logger.success(
        f"Successfully created an account for {discord_user.name} using the username {username}."
    )


async def prompt_user(
    bot: commands.Bot,
    discord_member: discord.Member,
    message: str,
) -> str:
    """Prompt user to respond to a question via private message"""
    await discord_member.send(f"{message}")

    try:

        def check(m):
            # Make sure we're only listening for a message from the relevant user via DM
            return m.author == discord_member and isinstance(
                m.channel, discord.DMChannel
            )

        message: discord.Message = await bot.wait_for(
            "message", timeout=60.0, check=check
        )

    except TimeoutError:
        logger.info(f"Timed out awaiting reply from {discord_member.name}.")

    else:
        await message.add_reaction("👍")
        return message.content


async def send_user_account_details(
    bot: commands.bot,
    discord_user: discord.User,
    remove_greeting: bool = False,
):
    """
    Send a Discord user their 2HOL account details.

    Greeting optional for cases where we just want the details, such as initial creation.
    """

    account_details = get_user_by_discord_id(discord_user.id)

    if account_details is None:
        # TODO: Profile this path, quite slow in dev env from CX UI.
        return await create_user(bot, discord_user)

    message_greeting = f"Hey {discord_user.mention}! Here are your account details:"
    message_details = (
        f"\n**Username:** `{account_details[0]}`\n**Key:** `{account_details[1]}`"
    )

    try:
        await discord_user.send(
            message_details if remove_greeting else message_greeting + message_details
        )

    except discord.Forbidden:
        # TODO: Does this still raise for cases calling this function?
        # TODO: Some nice handling for the

        pass
