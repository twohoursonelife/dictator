import socket
from dataclasses import dataclass
from datetime import date
from typing import cast

import discord
import inflect
from discord import app_commands
from discord.ext import commands, tasks

from dictator.logger_config import logger
from dictator.open_collective import ForecastOpenCollective
from dictator.settings import config


class PlayerListError(ValueError):
    """Raised when the game server returns an invalid PLAYER_LIST message."""


@dataclass(frozen=True, slots=True)
class Player:
    """A player record returned by the games PLAYER_LIST message."""

    player_id: int
    eve_id: int
    parent_id: int
    gender: str
    age: float
    declared_infertile: bool
    is_tutorial: bool
    name: str
    family_name: str


@dataclass(frozen=True, slots=True)
class PlayerListResponse:
    """Server version and players used by game stats."""

    required_version: str
    player_count: int
    players: list[Player]


type Family = list[Player]


class Stats(commands.Cog):
    FAMILY_SEPARATOR = "――――――――――"

    def __init__(self, dictator: commands.Bot) -> None:
        self.dictator = dictator
        self.p = inflect.engine()

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """Configure channels and start the appropriate background tasks."""
        self.OC_CHANNEL = cast(
            discord.TextChannel,
            self.dictator.get_channel(config.OC_CHANNEL_ID),
        )

        if self.OC_CHANNEL:
            if not self.open_collective_forecast.is_running():
                self.open_collective_forecast.start()

        else:
            logger.warning("Unable to find OC Channel, not starting OC stats.")

        self.STATS_CHANNEL = cast(
            discord.TextChannel,
            self.dictator.get_channel(config.STATS_CHANNEL_ID),
        )

        if self.STATS_CHANNEL:
            if not self.stats_loop.is_running():
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
        """Check that the live stats loop is still running and restart it if needed."""
        if self.stats_loop.is_running():
            logger.debug("Stats loop running successfully!")
        else:
            logger.error("Stats loop not running, trying to start it!")
            self.stats_loop.start()

    @tasks.loop(minutes=1)
    async def stats_loop(self) -> None:
        await self.update_stats()

    @stats_loop.before_loop
    async def before_stats_loop(self) -> None:
        await self.dictator.wait_until_ready()
        self.STATS_MESSAGE = await self.reset_stats_channel(self.STATS_CHANNEL)

    async def reset_stats_channel(
        self, channel: discord.TextChannel
    ) -> discord.Message:
        """Delete the previous bot stats message and create a loading message."""
        async for msg in channel.history(limit=1):
            if msg.author == self.dictator.user:
                await msg.delete()

        return await channel.send(
            embed=discord.Embed(
                title="Live server stats loading...", colour=config.MAIN_COLOUR
            )
        )

    async def update_stats(self) -> None:
        """Fetch current game stats and update the live stats message."""
        try:
            server_version, player_count, family_message = await self.get_server_stats()
        except Exception as e:  # noqa: BLE001 - failures should show offline state
            logger.error(f"Failed to get server stats: {e}")
            embed = discord.Embed(
                title="Server is offline", colour=discord.Colour.red()
            )
            embed.timestamp = discord.utils.utcnow()
            await self.STATS_MESSAGE.edit(embed=embed)
            return

        bot_version = config.DICTATOR_VERSION[:6]

        embed = discord.Embed(title="Stats", colour=config.MAIN_COLOUR)
        embed.add_field(name="Players", value=str(player_count))
        embed.add_field(name="Families", value=family_message, inline=False)
        embed.add_field(
            name="",
            value=f"-# `Server v{server_version}`\n-# `Dictator v{bot_version.upper()}`",
            inline=False,
        )
        embed.timestamp = discord.utils.utcnow()

        await self.STATS_MESSAGE.edit(embed=embed)

    async def get_server_stats(self) -> tuple[str, int, str]:
        """Return the server version, player count, and complete family message."""
        player_list = await self.player_list_request()

        family_message = self.format_families(player_list.players)

        return player_list.required_version, player_list.player_count, family_message

    async def player_list_request(self) -> PlayerListResponse:
        """
        A successful response will be formatted like so:

        SN
        current_players/max_players
        challenge_string
        required_version_number
        #num_players
        player_id,eve_id,parent_id,gender,age,declaredInfertile,isTutorial,name,family_name
        ...
        #
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2)
            s.connect(("play.twohoursonelife.com", 8005))
            if config.PLAYER_LIST_PASSWORD:
                s.sendall(f"PLAYER_LIST {config.PLAYER_LIST_PASSWORD}#".encode())
            else:
                s.sendall(b"PLAYER_LIST#")

            data_bytes = []
            messages_received = 0
            while True:
                try:
                    chunk = s.recv(1024)

                except TimeoutError:
                    break

                else:
                    if not chunk:
                        break  # sudden disconnect
                    data_bytes.append(chunk)
                    messages_received += chunk.count(ord("#"))
                    if messages_received >= 2:  # SN and PLAYER_LIST
                        break

            player_list = b"".join(data_bytes).decode("utf-8")

        return self.parse_player_list(player_list)

    def parse_player_list(self, player_list: str) -> PlayerListResponse:
        """Validate the PLAYER_LIST response from the server and decode players."""
        if not player_list.endswith("#"):
            raise PlayerListError("PLAYER_LIST message is incomplete!")

        messages = player_list.split("#")[:-1]
        if any(message.strip() == "REJECTED" for message in messages):
            raise PlayerListError(
                "PLAYER_LIST message returned REJECTED, check password!"
            )

        try:
            server_info, player_data = messages
            message_type, _current_players, _challenge, required_version = (
                server_info.splitlines()
            )
            if message_type != "SN":
                raise ValueError("Expected SN message")

            count, *player_rows = player_data.splitlines()
            player_count = int(count)
            players = []
            for row in player_rows:
                (
                    player_id,
                    eve_id,
                    parent_id,
                    gender,
                    age,
                    declared_infertile,
                    is_tutorial,
                    name,
                    family_name,
                ) = row.split(",")
                players.append(
                    Player(
                        player_id=int(player_id),
                        eve_id=int(eve_id),
                        parent_id=int(parent_id),
                        gender=gender,
                        age=float(age),
                        declared_infertile=declared_infertile == "1",
                        is_tutorial=is_tutorial == "1",
                        name=name,
                        family_name=family_name,
                    )
                )
            if player_count != len(players):
                raise ValueError("Player count does not match the response rows")

            return PlayerListResponse(required_version, player_count, players)
        except ValueError as error:
            raise PlayerListError("PLAYER_LIST message is malformed!") from error

    def is_solo_eve(self, family: Family) -> bool:
        """
        Identify an Eve who has declared infertility and is her lineage's only living player.
        Eve may have had children who died; this checks current players, not birth history.
        """
        return (
            len(family) == 1
            and family[0].player_id == family[0].eve_id
            and family[0].declared_infertile
        )

    def is_fertile(self, player: Player) -> bool:
        """
        A player is fertile if they are female, not declared infertile, and
        under 104 years old.

        A young player counts towards the fertile count as we explicitly follow
        the logic of the game clients HUD implementation here.
        """
        return (
            player.gender == "F" and not player.declared_infertile and player.age < 104
        )

    def is_tutorial_family(self, family: Family) -> bool:
        """Return whether a family is a single player in the tutorial."""
        return len(family) == 1 and family[0].is_tutorial

    def family_name(self, family: Family) -> str:
        """Return the display name used for a family in the stats message."""
        name = family[0].family_name.title()
        return name or "*Unnamed*"

    def format_families(self, players: list[Player]) -> str:
        """Group players by Eve ID and render family stats in input order."""
        grouped_families: dict[int, Family] = {}
        for player in players:
            grouped_families.setdefault(player.eve_id, []).append(player)
        family_list = grouped_families.values()

        active_families = []
        solo_eves = 0
        tutorial_players = 0
        for family in family_list:
            if self.is_tutorial_family(family):
                tutorial_players += 1
            elif self.is_solo_eve(family):
                solo_eves += 1
            else:
                active_families.append(
                    f"{len(family)} in {self.family_name(family)} "
                    f"({sum(self.is_fertile(player) for player in family)} fertile)"
                )

        message_lines = [
            f"{len(active_families)} active",
            self.FAMILY_SEPARATOR,
            *active_families,
        ]

        if family_list:
            message_lines.append(self.FAMILY_SEPARATOR)

        if solo_eves:
            message_lines.append(
                f"{solo_eves} playing as solo {self.p.plural('Eve', solo_eves)}"
            )

        if tutorial_players:
            message_lines.append(f"{tutorial_players} playing the tutorial")

        if solo_eves or tutorial_players:
            message_lines.append(self.FAMILY_SEPARATOR)

        return "\n".join(message_lines) + "\n"

    def open_collective_forecast_embed(self) -> discord.Embed:
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
        """Send the Open Collective forecast on the configured calendar day."""
        if date.today().day != config.OC_FORECAST_MONTH_DAY:  # noqa: DTZ011 - server-local calendar day
            return

        embed = self.open_collective_forecast_embed()
        await self.OC_CHANNEL.send(embed=embed)

    @app_commands.command()
    @app_commands.guild_only()
    @app_commands.checks.has_role(config.MOD_ROLE_ID)
    async def open_collective(self, interaction: discord.Interaction) -> None:
        """Generates and sends Open Collective forecast to the current channel."""
        await interaction.response.defer()

        embed = self.open_collective_forecast_embed()
        await interaction.followup.send(embed=embed)


async def setup(dictator: commands.Bot) -> None:
    await dictator.add_cog(Stats(dictator))
