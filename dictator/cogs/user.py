import re
from typing import cast

import discord
from discord import app_commands
from discord.ext import commands

from dictator.db_manager import db_connection as db_conn
from dictator.logger_config import logger
from dictator.settings import config
from dictator.utilities import (
    create_user,
    generate_login_key,
    send_user_account_details,
)


def format_account_age_limit(minimum_age_days: int) -> str:
    if minimum_age_days == 0:
        return "Disabled"

    unit = "day" if minimum_age_days == 1 else "days"
    return f"{minimum_age_days} {unit}"


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

        # Bots bypass verification, we also don't want to create accounts for them.
        if member.bot:
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

    @app_commands.command()
    @app_commands.guild_only()
    @app_commands.checks.has_role(config.ADMIN_ROLE_ID)
    @app_commands.describe(
        minimum_age_days="Minimum Discord account age in days; use 0 to disable"
    )
    async def account_age_limit(
        self,
        interaction: discord.Interaction,
        minimum_age_days: app_commands.Range[int, 0, 365] | None = None,
    ) -> None:
        """View or change the live Discord account age requirement."""
        current_age_days = config.MIN_DISCORD_ACCOUNT_AGE_DAYS

        if minimum_age_days is None:
            await interaction.response.send_message(
                f"The minimum Discord account age is currently "
                f"**{format_account_age_limit(current_age_days)}**.",
                ephemeral=True,
            )
            return

        if minimum_age_days == current_age_days:
            await interaction.response.send_message(
                f"The minimum Discord account age is already "
                f"**{format_account_age_limit(current_age_days)}**.",
                ephemeral=True,
            )
            return

        config.MIN_DISCORD_ACCOUNT_AGE_DAYS = minimum_age_days
        await interaction.response.send_message(
            f"Changed the minimum Discord account age from "
            f"**{format_account_age_limit(current_age_days)}** to "
            f"**{format_account_age_limit(minimum_age_days)}**. "
            "This live override will reset to the configured default when the bot restarts.",
            ephemeral=True,
        )

        embed = discord.Embed(
            title="Account age restriction changed",
            colour=discord.Colour.orange(),
        )
        embed.set_author(
            name=str(interaction.user),
            icon_url=interaction.user.display_avatar.url,
        )
        embed.add_field(
            name="Previous:",
            value=format_account_age_limit(current_age_days),
            inline=True,
        )
        embed.add_field(
            name="New:",
            value=format_account_age_limit(minimum_age_days),
            inline=True,
        )
        embed.add_field(name="Persistence:", value="Until bot restart", inline=True)

        action_log_channel = cast(
            discord.abc.Messageable | None,
            self.dictator.get_channel(config.ACTION_LOG_CHANNEL_ID),
        )
        if action_log_channel is None:
            logger.error(
                "Could not audit an account age restriction change because the "
                f"action log channel ({config.ACTION_LOG_CHANNEL_ID}) was not found."
            )
        else:
            try:
                await action_log_channel.send(embed=embed)
            except discord.HTTPException:
                logger.exception("Failed to audit an account age restriction change.")

        logger.info(
            f"{interaction.user} changed the minimum Discord account age from "
            f"{current_age_days} to {minimum_age_days} days."
        )

    # Support users who continue to find mention of -key in online resources.
    @commands.command(brief="Legacy account details command. Use /account instead.")
    async def key(self, ctx: commands.Context) -> None:
        if not isinstance(ctx.channel, discord.channel.DMChannel):
            await ctx.message.delete()

        logger.info(f"{ctx.author} used the legacy -key command.")
        await send_user_account_details(self.dictator, ctx.author)

    @commands.command(
        brief="Create multiple bot accounts",
        help="Create a game account not attached to a Discord user",
        usage="<user>",
    )
    @commands.guild_only()
    @commands.has_role(config.ADMIN_ROLE_ID)
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
