from dataclasses import dataclass

import discord
from discord import app_commands
from discord.ext import commands

from dictator.constants import EXP_CHANNEL_ID, GENERAL_CHANNEL_ID, VET_CHANNEL_ID
from dictator.utilities import (
    already_has_role,
    assign_role,
    get_playtime_hours,
)


@dataclass
class Role:
    """A structured object to hold role data."""

    name: str
    hours: int


ROLE_1 = Role(name="Not Completely Lost", hours=10)
ROLE_2 = Role(name="Well Experienced", hours=50)
ROLE_3 = Role(name="Veteran", hours=375)
ROLE_4 = Role(name="What is life?", hours=1000)


@dataclass
class RoleData:
    """A structured object to hold data for role claim commands."""

    name: str
    hours: int
    failure_message: str
    announcement_channel_id: int
    success_message: str


class Roles(commands.Cog):
    def __init__(self, dictator: commands.Bot) -> None:
        self.dictator = dictator

    async def _handle_role_claim(
        self, interaction: discord.Interaction, role_data: RoleData
    ):
        """A helper function to handle the logic for claiming a role."""
        await interaction.response.defer(ephemeral=True)

        if already_has_role(interaction.user, role_data.name):
            await interaction.followup.send(
                f"{interaction.user.mention}, you already have this role!",
                ephemeral=True,
            )
            return

        if get_playtime_hours(interaction.user.id) < role_data.hours:
            await interaction.followup.send(
                f"{interaction.user.mention}, you do not have {role_data.hours} or more hours in game. {role_data.failure_message}",
                ephemeral=True,
            )
            return

        await assign_role(
            interaction, role_data.name, "User claimed role via Dictator command."
        )

        channel = self.dictator.get_channel(role_data.announcement_channel_id)
        await channel.send(role_data.success_message)

        await interaction.followup.send(
            f"You now have the {role_data.name} role.", ephemeral=True
        )

    @app_commands.command()
    @app_commands.guild_only()
    async def ncl(self, interaction: discord.Interaction) -> None:
        """Claims the NCL role if you have 10 or more hours in game. Grants you more access to the server."""
        role_info = RoleData(
            name=ROLE_1.name,
            hours=ROLE_1.hours,
            failure_message="Nearly!",
            announcement_channel_id=GENERAL_CHANNEL_ID,
            success_message=f"Woohoo, {interaction.user.mention}! You have claimed the '{ROLE_1.name}' role, for playing {ROLE_1.hours} or more hours in game! *You're starting to know your way around!*",
        )
        await self._handle_role_claim(interaction, role_info)

    @app_commands.command()
    @app_commands.guild_only()
    async def exp(self, interaction: discord.Interaction) -> None:
        """Claims the EXP role if you have 50 or more hours in game. Grants you more access to the server."""
        role_info = RoleData(
            name=ROLE_2.name,
            hours=ROLE_2.hours,
            failure_message="Keep on playin'!",
            announcement_channel_id=EXP_CHANNEL_ID,
            success_message=f"Congratulations, {interaction.user.mention}! You have claimed the '{ROLE_2.name}' role, for playing {ROLE_2.hours} or more hours in game! *Go take a break!*",
        )
        await self._handle_role_claim(interaction, role_info)

    @app_commands.command()
    @app_commands.guild_only()
    async def vet(self, interaction: discord.Interaction) -> None:
        """Claims the VET role if you have 375 or more hours in game. Grants you more access to the server."""
        role_info = RoleData(
            name=ROLE_3.name,
            hours=ROLE_3.hours,
            failure_message="Surely just a few more to go...!",
            announcement_channel_id=VET_CHANNEL_ID,
            success_message=f"Woah, {interaction.user.mention}! You have claimed the '{ROLE_3.name}' role, for playing {ROLE_3.hours} or more hours in game! *Your a part of the furniture now*",
        )
        await self._handle_role_claim(interaction, role_info)

    @app_commands.command()
    @app_commands.guild_only()
    async def wil(self, interaction: discord.Interaction) -> None:
        """Claims the WIL role if you have 1,000 or more hours in game. Grants you more access to the server."""
        role_info = RoleData(
            name=ROLE_4.name,
            hours=ROLE_4.hours,
            failure_message="Just around the corner, *right?*",
            announcement_channel_id=VET_CHANNEL_ID,
            success_message=f"Woah, {interaction.user.mention}! You have claimed the '{ROLE_4.name}' role, for playing {ROLE_4.hours} or more hours in game! *I suppose you can go now*",
        )
        await self._handle_role_claim(interaction, role_info)


async def setup(dictator: commands.Bot) -> None:
    await dictator.add_cog(Roles(dictator))
