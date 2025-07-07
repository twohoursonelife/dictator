import re

import discord
from discord import app_commands
from discord.ext import commands

from dictator.constants import GAME_MOD_ROLE_ID
from dictator.db_manager import db_connection as db_conn
from dictator.logger_config import logger
from dictator.utilities import (
    create_user,
    generate_login_key,
    send_user_account_details,
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
            await create_user(self.dictator, member_after)

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
        await create_user(self.dictator, member)

    @app_commands.command()
    async def account(self, interaction: discord.Interaction) -> None:
        """Get or create your game log in information."""
        await interaction.response.send_message(
            "I'll send you a message with your account details!",
            ephemeral=True,
            delete_after=10,
        )

        await send_user_account_details(self.dictator, interaction.user)

    # Legacy sadness <3
    @commands.command(brief="Legacy account details command.")
    async def key(self, ctx: commands.Context) -> None:
        await ctx.message.delete()
        logger.info(f"{ctx.author} used the legacy -key command.")
        await send_user_account_details(self.dictator, ctx.author)

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
