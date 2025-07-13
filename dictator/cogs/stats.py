import socket
from datetime import date

import discord
import inflect
from discord import app_commands
from discord.ext import commands, tasks

from dictator.constants import (
    DICTATOR_VERSION,
    MAIN_COLOUR,
    MOD_ROLE_ID,
    OC_CHANNEL_ID,
    OC_FORECAST_MONTH_DAY,
    PLAYER_LIST_PASSWORD,
    STATS_CHANNEL_ID,
)
from dictator.logger_config import logger
from dictator.open_collective import ForecastOpenCollective


class Stats(commands.Cog):
    def __init__(self, dictator: commands.Bot) -> None:
        self.dictator = dictator
        self.p = inflect.engine()

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        self.OC_CHANNEL: discord.TextChannel = self.dictator.get_channel(OC_CHANNEL_ID)

        if self.OC_CHANNEL:
            if not self.open_collective_forecast.is_running():
                self.open_collective_forecast.start()

        else:
            logger.warning("Unable to find OC Channel, not starting OC stats.")

        self.STATS_CHANNEL: discord.TextChannel = self.dictator.get_channel(
            STATS_CHANNEL_ID
        )

        if self.STATS_CHANNEL:
            if not self.stats_loop.is_running():
                # TODO: Use a before loop call instead of manual setup
                self.STATS_MESSAGE = await self.reset_stats_channel(self.STATS_CHANNEL)
                self.stats_loop.start()
            else:
                logger.info("Stats loop already running!")
        else:
            logger.warning("Unable to find Stats Channel, not starting player stats.")

        self.loop_checker.start()

    def cog_unload(self):
        self.open_collective_forecast.cancel()
        self.stats_loop.cancel()
        self.loop_checker.cancel()

    @tasks.loop(hours=1)
    async def loop_checker(self) -> None:
        if self.stats_loop.is_running():
            logger.debug("Stats loop running successfully!")
        else:
            logger.error("Stats loop not running, trying to start it!")
            self.stats_loop.start()

    @tasks.loop(minutes=1)
    async def stats_loop(self) -> None:
        await self.update_stats()

    async def reset_stats_channel(
        self, channel: discord.TextChannel
    ) -> discord.Message:
        async for msg in channel.history(limit=1):
            if msg.author == self.dictator.user:
                await msg.delete()

        return await channel.send(
            embed=discord.Embed(
                title="Live server stats loading...", colour=MAIN_COLOUR
            )
        )

    async def update_stats(self) -> None:
        server_info, families, family_count = await self.get_server_stats()
        bot_version = (
            DICTATOR_VERSION if not len(DICTATOR_VERSION) >= 6 else DICTATOR_VERSION[:6]
        )

        embed = discord.Embed(title="Stats", colour=MAIN_COLOUR)
        embed.add_field(name="Players", value=server_info[2])
        embed.add_field(
            name="Families", value=f"{family_count} total\n{families}", inline=False
        )
        embed.add_field(
            name="",
            value=f"-# `Server v{server_info[1]}`\n-# `Dictator v{bot_version}`",
            inline=False,
        )
        embed.timestamp = discord.utils.utcnow()

        await self.STATS_MESSAGE.edit(embed=embed)

    async def get_server_stats(self) -> str:
        result = await self.player_list_request()
        await self.verify_player_list(result)
        server_info, parsed_player_list = await self.parse_player_list(result)

        family_list = await self.group_families(parsed_player_list)
        formatted_families = await self.format_family_list(family_list)

        family_count = len(family_list)

        return server_info, formatted_families, family_count

    async def player_list_request(self) -> str:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2)
            s.connect(("play.twohoursonelife.com", 8005))
            if PLAYER_LIST_PASSWORD:
                s.sendall(f"PLAYER_LIST {PLAYER_LIST_PASSWORD}#".encode("utf-8"))
            else:
                s.sendall(
                    "PLAYER_LIST#".encode("utf-8")
                )  # format changes if no password

            data_bytes = []
            messages_received = 0
            while True:
                try:
                    chunk = s.recv(1024)

                except TimeoutError:
                    break

                else:
                    if not chunk or chunk == b"":
                        break  # sudden disconnect
                    data_bytes.append(chunk)
                    messages_received += chunk.count(ord("#"))
                    if messages_received >= 2:  # SN and PLAYER_LIST
                        break

            player_list = b"".join(data_bytes).decode("utf-8")

        return player_list

    async def verify_player_list(self, player_list: str) -> bool:
        if "#" != player_list[-1]:
            raise Exception("PLAYER_LIST message is incomplete!")

        if "REJECTED" in player_list:
            raise Exception("PLAYER_LIST message returned REJECTED, check password!")

        return True

    async def parse_player_list(self, player_list: str) -> tuple:
        # Convert to list and remove trailing hash char
        player_list = player_list.split("\n")[:-1]

        # "#23" -> "23"
        player_list[4] = player_list[4][1:]

        # Remove irrelevant data
        player_list.pop(2)
        player_list.pop(0)

        players = [player.split(",") for player in player_list[3:]]

        return player_list[:3], players

    async def group_families(self, parsed_player_list: str) -> str:
        grouped_families = {}
        for player in parsed_player_list:
            eve_id = int(player[1])
            if eve_id not in grouped_families:
                grouped_families[eve_id] = []
            grouped_families[eve_id] += [player]

        return list(grouped_families.values())

    async def format_family_list(self, family_list: str) -> str:
        # TODO
        # What if formatted_families was a list?
        # Then we can sort() it descending before
        # Returning a list comprhension, joining
        # all items into a formatted string
        # as shown by mig
        formatted_families = []
        formatted_families = "――――――――――\n"
        solo_eves = 0
        tutorial_players = 0
        unnamed_families = 0
        unnamed_family_players = 0
        for family in family_list:
            # TODO
            # We can extract family_name into a recursive function
            # where we loop the family until we find a surname
            # and apply other relevant naming rules

            first_player = family[0]
            (
                player_id,
                eve_id,
                parent_id,
                gender,
                age,
                declaredInfertile,
                isTutorial,
                name,
                family_name,
            ) = first_player

            family_name = family_name.title()

            if len(family) == 1:
                if isTutorial == "1":
                    tutorial_players += 1
                    continue

                if player_id == eve_id and declaredInfertile == "1":
                    solo_eves += 1
                    continue

            if not family_name:
                unnamed_families += 1
                unnamed_family_players += len(family)
                continue
            formatted_families += f"{len(family)} in {family_name}\n"

        if len(family_list):
            formatted_families += "――――――――――\n"

        if unnamed_families:
            formatted_families += f"{unnamed_family_players} in {unnamed_families} unnamed {self.p.plural('family', unnamed_families)}\n"

        if solo_eves:
            formatted_families += f"{solo_eves} playing as solo Eves\n"

        if tutorial_players:
            formatted_families += f"{tutorial_players} playing the tutorial\n"

        if unnamed_families or solo_eves or tutorial_players:
            formatted_families += "――――――――――\n"

        return formatted_families

    async def open_collective_forecast_embed(self) -> discord.Embed:
        forecast = ForecastOpenCollective.forecast()
        description = (
            f"**TLDR:** Sufficient funding until **{forecast['forecast_continued_income']}**"
            f"\n\n**Details:** Assuming expenses remain similar and:"
            f"\n- assuming we receive **no future income**, we have funding until **{forecast['forecast_no_income']}**"
            f"\n- assuming **average donations continue**, we have funding until **{forecast['forecast_continued_income']}**"
            f"\n\n**Current balance: {forecast['current_balance']}**"
            f"\n\n**Data time period: past {forecast['analysis_period_months']} months. This is only a forecast and is likely to change. Forecast is up to a max of 5 years.*"
        )

        return discord.Embed(
            title="Summary of 2HOL Open Collective finances:",
            description=description,
            colour=0x37FF77,
        )

    @tasks.loop(hours=24)
    async def open_collective_forecast(self) -> None:
        if date.today().day != OC_FORECAST_MONTH_DAY:
            return

        embed = await self.open_collective_forecast_embed()
        await self.OC_CHANNEL.send(embed=embed)

    @app_commands.command()
    @app_commands.guild_only()
    @app_commands.checks.has_role(MOD_ROLE_ID)
    async def open_collective(self, interaction: discord.Interaction) -> None:
        """Generates and sends Open Collective forecast to the current channel."""
        await interaction.response.defer()

        embed = await self.open_collective_forecast_embed()
        await interaction.followup.send(embed=embed)


async def setup(dictator: commands.Bot) -> None:
    await dictator.add_cog(Stats(dictator))
