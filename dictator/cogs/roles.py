import discord
from discord import app_commands
from discord.ext import commands
from db_manager import db_connection as db_conn

# Roles ["Role name, must match Discord", Required hours]
ROLE_1 = {"name": "Not Completely Lost", "hours": 10}
ROLE_2 = {"name": "Well Experienced", "hours": 50}
ROLE_3 = {"name": "Veteran", "hours": 375}
ROLE_4 = {"name": "What is life?", "hours": 1000}


class Roles(commands.Cog):
    def __init__(self, dictator: commands.Bot) -> None:
        self.dictator = dictator

    @app_commands.command()
    async def ncl(self, interaction: discord.Interaction) -> None:
        """Claims the NCL role if you have 10 or more hours in game. Grants you more access to the server."""
        await interaction.response.defer(ephemeral=True)

        if self.already_has_role(interaction, ROLE_1["name"]):
            await interaction.followup.send(
                f"{interaction.user.mention}, you already have this role!",
                ephemeral=True,
            )
            return

        if self.playtime_less_than(interaction.user.id, ROLE_1["hours"] * 60):
            await interaction.followup.send(
                f'{interaction.user.mention}, you do not have {ROLE_1["hours"]} or more hours in game. Nearly!',
                ephemeral=True,
            )
            return

        await self.assign_role(interaction, ROLE_1["name"], "User claimed role")
        await interaction.followup.send(
            f'Woohoo, {interaction.user.mention}! You have claimed the \'{ROLE_1["name"]}\' role, for playing {ROLE_1["hours"]} or more hours in game! *You\'re starting to know your way around!*'
        )

    @app_commands.command()
    async def exp(self, interaction: discord.Interaction) -> None:
        """Claims the EXP role if you have 50 or more hours in game. Grants you more access to the server."""
        await interaction.response.defer(ephemeral=True)

        if self.already_has_role(interaction, ROLE_2["name"]):
            await interaction.followup.send(
                f"{interaction.user.mention}, you already have this role!",
                ephemeral=True,
            )
            return

        if self.playtime_less_than(interaction.user.id, ROLE_2["hours"] * 60):
            await interaction.followup.send(
                f'{interaction.user.mention}, you do not have {ROLE_2["hours"]} or more hours in game. Keep on playin!',
                ephemeral=True,
            )
            return

        await self.assign_role(interaction, ROLE_2["name"], "User claimed role")
        await interaction.followup.send(
            f'Congratulations, {interaction.user.mention}! You have claimed the \'{ROLE_2["name"]}\' role, for playing {ROLE_2["hours"]} or more hours in game! *Go take a break!*'
        )

    @app_commands.command()
    async def vet(self, interaction: discord.Interaction) -> None:
        """Claims the VET role if you have 375 or more hours in game. Grants you more access to the server."""
        await interaction.response.defer(ephemeral=True)

        if self.already_has_role(interaction, ROLE_3["name"]):
            await interaction.followup.send(
                f"{interaction.user.mention}, you already have this role!",
                ephemeral=True,
            )
            return

        if self.playtime_less_than(interaction.user.id, ROLE_3["hours"] * 60):
            await interaction.followup.send(
                f'{interaction.user.mention}, you do not have {ROLE_3["hours"]} or more hours in game. Surely just a few more to go...!',
                ephemeral=True,
            )
            return

        await self.assign_role(interaction, ROLE_3["name"], "User claimed role")
        await interaction.followup.send(
            f'Woah, {interaction.user.mention}! You have claimed the \'{ROLE_3["name"]}\' role, for playing {ROLE_3["hours"]} or more hours in game! *You\'re apart of the furniture now*'
        )

    @app_commands.command()
    async def wil(self, interaction: discord.Interaction) -> None:
        """Claims the WIL role if you have 1,000 or more hours in game. Grants you more access to the server."""
        await interaction.response.defer(ephemeral=True)

        if self.already_has_role(interaction, ROLE_4["name"]):
            await interaction.followup.send(
                f"{interaction.user.mention}, you already have this role! Doh!",
                ephemeral=True,
            )
            return

        if self.playtime_less_than(interaction.user.id, ROLE_4["hours"] * 60):
            await interaction.followup.send(
                f'{interaction.user.mention}, you do not have {ROLE_4["hours"]} or more hours in game. Just around the corner, *right?*',
                ephemeral=True,
            )
            return

        await self.assign_role(interaction, ROLE_4["name"], "User claimed role")
        await interaction.followup.send(
            f'Woah, {interaction.user.mention}! You have claimed the \'{ROLE_4["name"]}\' role, for playing {ROLE_4["hours"]} or more hours in game! *I suppose you can go now*'
        )

    def already_has_role(self, interaction: discord.Interaction, role) -> bool:
        role_object = discord.utils.get(interaction.user.roles, name=role)
        if role_object != None:
            return True
        return False

    async def assign_role(self, interaction: discord.Interaction, role, reason) -> None:
        role_object = discord.utils.get(interaction.guild.roles, name=role)
        await interaction.user.add_roles(role_object, reason=reason)

    def playtime_less_than(
        self, discord_id: discord.User.id, less_than_minutes: int
    ) -> bool:
        with db_conn() as db:
            db.execute(
                f"SELECT time_played FROM ticketServer_tickets WHERE discord_id = {discord_id}"
            )
            time_played = db.fetchone()

        return True if int(time_played[0]) < less_than_minutes else False


async def setup(dictator: commands.Bot) -> None:
    await dictator.add_cog(Roles(dictator))
