import discord
from discord import app_commands
from discord.ext import commands

from db_manager import db_connection as db_conn
from datetime import timezone
import math


class Informational(commands.Cog):
    def __init__(self, dictator: commands.Bot) -> None:
        self.dictator = dictator

    @app_commands.command()
    async def rtfm(self, interaction: discord.Interaction) -> None:
        """Sends basic infoamtion about playing for the first time."""

        await interaction.response.send_message(
            f'How do I play?\nHow do I download?\n\nHeres the manual to play for the first time\n<https://twohoursonelife.com/first-time-playing/?ref=rtfm>\n\nCheck your messages from me to find your username and password.\n*Can\'t find the message? Use the "/account" command.*'
        )

    @app_commands.guild_only()
    @app_commands.command()
    async def info(self, interaction: discord.Interaction, discord_user: discord.User) -> None:
        """Privately displays you information about the specified user. Input a Discord User like object, such as a username, nickname, ID or formatted mention."""
        await interaction.response.defer(ephemeral=True)

        with db_conn() as db:
            db.execute(
                f"SELECT ticketServer_tickets.email, blocked, game_count, last_game_date, game_total_seconds FROM ticketServer_tickets INNER JOIN reviewServer_user_stats ON reviewServer_user_stats.email = ticketServer_tickets.email WHERE discord_id = '{discord_user.id}'"
            )
            user_info = db.fetchone()

        if not user_info:
            embed = discord.Embed(
                title=f"'{discord_user.name}' either has not lived any lives yet or does not have an account.", colour=0xFFBB35
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        member = interaction.guild.get_member(discord_user.id)
        last_active = user_info[3].replace(tzinfo=timezone.utc)

        # Form embed
        embed = discord.Embed(
            title=f"Results for the user '{discord_user.name}':", colour=0xFFBB35
        )
        
        # Round down time played so as not to mislead when users are checking for a milestone
        embed.add_field(
            name="Time played:",
            value=f"{math.floor(user_info[4] / 60 / 60):,}h {math.floor(user_info[4] / 60 % 60):,}m",
        )
        embed.add_field(name="Blocked:", value="Yes" if user_info[1] else "No")
        embed.add_field(
            name="Joined guild:",
            value=f"{discord.utils.format_dt(member.joined_at, 'R')}"
            if member
            else "Unknown",
        )
        embed.add_field(name="Game username:", value=user_info[0])
        embed.add_field(
            name="Last activity:", value=f"{discord.utils.format_dt(last_active, 'R')}"
        )
        embed.set_footer(text="Data range: August 2019 - Current")
        await interaction.followup.send(embed=embed, ephemeral=True)


async def setup(dictator: commands.Bot) -> None:
    await dictator.add_cog(Informational(dictator))
