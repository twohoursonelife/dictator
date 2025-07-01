import re

import discord
from constants import DEBUG_CHANNEL_ID, GAME_MOD_ROLE_ID
from db_manager import db_connection as db_conn
from discord import app_commands
from discord.ext import commands
from exceptions import (
    UserAlreadyRegisteredError,
    UsernameAlreadyExistsError,
    UsernameValidationError,
)
from logger_config import logger
from utils.utils import (
    generate_login_key,
    get_user_by_discord_id,
    is_new_discord_user,
    is_unique_username,
    is_user_already_registered,
    is_valid_username,
)


# TODO: If user sends a DM, respond with info.
class User(commands.Cog):
    def __init__(self, dictator: commands.Bot) -> None:
        self.dictator = dictator

    @commands.Cog.listener()
    async def on_member_update(
        self,
        member_before: discord.Member,
        member_after: discord.Member,
    ) -> None:
        """Trigger account creation after member verification (rules acceptance)."""
        if member_before.pending and not member_after.pending:
            logger.debug(f"{member_after.name} pending state changed.")
            await self.create_user(member_after)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        """
        Trigger account creation if member verification (rules acceptance) is disabled.
        This is applicable during development or future configuration changes.
        """

        if member.pending:
            logger.debug(f"{member.name} joined the server, in pending state.")
            return

        logger.info(f"{member.name} joined the server, not in pending state.")
        await self.create_user(member)

    @app_commands.command()
    async def account(self, interaction: discord.Interaction) -> None:
        """Get or create your game log in information."""
        await interaction.response.send_message(
            "I'll send you a message with your account details!",
            ephemeral=True,
            delete_after=15,
        )

        await self.send_user_account_details(interaction.user)

    # Legacy sadness <3
    @commands.command(brief="Legacy account details command.")
    async def key(self, ctx: commands.Context) -> None:
        await ctx.message.delete()
        logger.info(f"{ctx.author} used the legacy -key command.")
        await self.send_user_account_details(ctx.author)

    async def send_user_account_details(
        self,
        discord_user: discord.User,
        remove_greeting: bool = False,
    ):
        """
        Send a Discord user their 2HOL account details.

        Greeting optional for cases where we just want the details, such as initial creation.
        """

        account_details = get_user_by_discord_id(discord_user.id)

        if account_details is None:
            return await self.create_user(discord_user)

        message_greeting = f"Hey {discord_user.mention}! Here are your account details:"
        message_details = (
            f"\n**Username:** `{account_details[0]}`\n**Key:** `{account_details[1]}`"
        )

        await discord_user.send(
            message_details if remove_greeting else message_greeting + message_details,
            delete_after=300,
        )

    async def create_user(
        self,
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
            return await self.send_user_account_details(discord_user)

        except UsernameValidationError as e:
            chosen_username = await self.prompt_user(
                discord_user,
                f"Hey {discord_user.mention}, there was an error when creating your 2HOL account:\n> {str(e)}\n\nPlease reply with a valid username.",
            )

            if chosen_username is None:
                return await discord_user.send(
                    "You didn't tell me what to use instead. Use the /account command when you're ready!"
                )

            return await self.create_user(discord_user, chosen_username)

        except UsernameAlreadyExistsError:
            chosen_username = await self.prompt_user(
                discord_user,
                f"Hey {discord_user.mention}, the username `{username}` is already in use. Please reply with another valid username.",
            )

            if chosen_username is None:
                return await discord_user.send(
                    "You didn't tell me what to use instead. Use the /account command when you're ready!"
                )

            return await self.create_user(discord_user, chosen_username)

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

            await self.send_user_account_details(discord_user, True)

        # TODO: Extract into generic handler
        except discord.Forbidden:
            notify_user = False

        else:
            notify_user = True

        # Audit
        # TODO: Extract audit log message into generic function
        debug_log_channel = self.dictator.get_channel(DEBUG_CHANNEL_ID)

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

    async def prompt_user(self, discord_member: discord.Member, message: str) -> str:
        """Prompt user to respond to a question via private message"""
        await discord_member.send(f"{message}")

        try:

            def check(m):
                # Make sure we're only listening for a message from the relevant user via DM
                return m.author == discord_member and isinstance(
                    m.channel, discord.DMChannel
                )

            message: discord.Message = await self.dictator.wait_for(
                "message", timeout=60.0, check=check
            )

        except TimeoutError:
            logger.info(f"Timed out awaiting reply from {discord_member.name}.")

        else:
            await message.add_reaction("👍")
            return message.content

    @commands.command(
        brief="Create multiple bot accounts",
        help="Create a game account not attached to a Discord user",
        usage="<user>",
    )
    @commands.guild_only()
    @commands.has_role(GAME_MOD_ROLE_ID)  # TODO: Admin
    async def create_bot(self, ctx, prefix, amount: int):
        await ctx.message.delete()

        # Filter prefix
        prefix = re.sub("[^a-zA-Z0-9]", "", prefix)

        for i in range(amount):
            username = f"{prefix}-{i}"
            key = generate_login_key()

            with db_conn() as db:
                db.execute(
                    "INSERT INTO ticketServer_tickets (email, login_key) VALUES (%s, %s)",
                    (username, key),
                )

            await ctx.author.send(f"{username} :: {key}")


async def setup(dictator: commands.Bot) -> None:
    await dictator.add_cog(User(dictator))
