import random
import re
from datetime import timedelta
from textwrap import wrap

import discord
from constants import DEBUG_CHANNEL_ID, GAME_MOD_ROLE_ID
from db_manager import db_connection as db_conn
from discord import app_commands
from discord.ext import commands
from logger_config import logger
from utils.utils import get_user_by_discord_id, get_user_by_username


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
            logger.debug(f"{member_after.named} pending state changed.")
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
        await interaction.response.defer(ephemeral=True)

        user = get_user_by_discord_id(interaction.user.id)

        if user is None:
            await interaction.followup.send(
                f"{interaction.user.mention} You don't have an account, I'm creating one for you now. I'll send you a message soon!",
                ephemeral=True,
            )
            logger.info(
                f"{interaction.user} attempted to retrieve their key but didn't have an account, we'll create them one."
            )
            await self.create_user(interaction.user)
            return

        username = user[0]
        key = user[1]
        await interaction.followup.send(
            f"Hey {interaction.user.mention}! Here is your login information:\n**Username:** `{username}`\n**Key:** `{key}`",
            ephemeral=True,
        )
        logger.success(f"Supplied username and key to {interaction.user}")

    async def create_user(self, user: discord.User, username: str = None) -> None:
        if username is None:
            username = user.name

        # Filter username, can't have any nasty characters
        # Then replaces any non whitlisted (regex) characters with empty string
        username = re.sub("[^a-zA-Z0-9]", "", username)

        if len(username) < 3:
            # Username was only made up of special chracters, prompt for one
            chosen_username = await self.prompt_user(
                user,
                f"Hey {user.mention}, your username doesn't contain enough valid characters. What should I use instead?",
            )

            if chosen_username is None:
                await user.send("You didn't tell me what to use instead.")
                return

            else:
                await self.create_user(user, chosen_username)
                return

        # Check if user already has an account before creating one
        check_user = get_user_by_discord_id(user.id)

        if check_user is not None:
            # User already has an account
            username = check_user[0]
            key = check_user[1]
            logger.info(
                f"We tried to create an account for {user} but they already had one, so we'll send them their login information."
            )
            await user.send(
                f"Hey {user.mention}, you already have an account! Here is your login information:\n**Username:** {username}\n**Key:** {key}"
            )
            return

        if len(username) > 32:
            username = username[0:32]

        # Check if username is already in use
        check_name = get_user_by_username(username)

        if check_name is not None:
            # Username is already in use, prompt for one
            chosen_username = await self.prompt_user(
                user,
                f"Hey {user.mention}, your username is already in use. What should I use instead?",
            )

            if chosen_username is None:
                await user.send("You didn't tell me what to use instead.")
                return

            else:
                await self.create_user(user, chosen_username)
                return

        # Create the users accounnt, calling on create_key for a key
        key = str(await self.create_key())
        user_id = int(user.id)
        username = str(username)

        with db_conn() as db:
            db.execute(
                f"INSERT INTO ticketServer_tickets (email, discord_id, login_key) VALUES ('{username}', '{user_id}', '{key}')"
            )

        # Notify the user
        try:
            await user.send(
                f"Welcome to 2HOL {user.mention}!\n"
                "\nPlease know that 2HOL is a moderated community."
                "\nWe only ask that you be kind to all players, as you would to a friend."
                "\nAll actions are recorded, please make a mod report in Discord if you have issues."
                "\nYou can read more on how to start playing [here](<https://twohoursonelife.com/first-time-playing?ref=create_acc>).\n"
                "\nWhen you're ready, you can use the details below to log in to the game:"
                f"\n**Username:** {username}"
                f"\n**Key:** {key}"
            )

        except Exception as e:
            notify_user = False
            logger.exception(e)

        else:
            notify_user = True

        one_week_ago = discord.utils.utcnow() - timedelta(weeks=1)
        new_discord_account = False
        if user.created_at > one_week_ago:
            new_discord_account = True

        debug_log_channel = self.dictator.get_channel(DEBUG_CHANNEL_ID)

        # Embed log
        embed = discord.Embed(
            title="New game account created", colour=discord.Colour.green()
        )
        embed.add_field(name="Member:", value=f"{user.mention}", inline=True)
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
                if new_discord_account
                else "Existing discord account"
            ),
            inline=True,
        )
        await debug_log_channel.send(embed=embed)

        logger.success(
            f"Successfully created an account for {user.name} using the username {username}."
        )

    # Generate a string consisting of 20 random chars, split into 4 chunks of 5 and seperated by -
    async def create_key(self) -> str:
        readable_base_32_digit_array = [
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "A",
            "B",
            "C",
            "D",
            "E",
            "F",
            "G",
            "H",
            "J",
            "K",
            "L",
            "M",
            "N",
            "P",
            "Q",
            "R",
            "S",
            "T",
            "U",
            "V",
            "W",
            "X",
            "Y",
            "Z",
        ]
        key = ""
        while len(key) != 20:
            key += readable_base_32_digit_array[
                random.randint(0, len(readable_base_32_digit_array) - 1)
            ]

        key_chunks = wrap(key, 5)
        key = "-".join(key_chunks)
        return key

    # Prompt user to respond to a question via private message
    async def prompt_user(self, user: discord.User, msg: str):
        await user.send(f"{msg}")
        try:

            def check(m):
                # Make sure we're only listening for a message from the relevant user via DM
                return m.author == user and isinstance(m.channel, discord.DMChannel)

            reply = await self.dictator.wait_for("message", timeout=60.0, check=check)

        except Exception as e:
            logger.exception(e)
            return

        else:
            return reply.content

    @commands.command(
        brief="Create multiple bot accounts",
        help="Create a game account not attached to a Discord user",
        usage="<user>",
    )
    @commands.guild_only()
    @commands.has_role(GAME_MOD_ROLE_ID)
    async def create_bot(self, ctx, prefix, amount: int):
        await ctx.message.delete()

        # Filter prefix
        prefix = re.sub("[^a-zA-Z0-9]", "", prefix)

        for i in range(amount):
            username = f"{prefix}-{i}"
            key = await self.create_key()

            with db_conn() as db:
                db.execute(
                    f"INSERT INTO ticketServer_tickets (email, login_key) VALUES ('{username}', '{key}')"
                )

            await ctx.author.send(f"{username} :: {key}")


async def setup(dictator: commands.Bot) -> None:
    await dictator.add_cog(User(dictator))
