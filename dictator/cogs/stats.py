import discord
from discord import app_commands

from discord.ext import commands, tasks

from open_collective import ForecastOpenCollective
from constants import STATS_CHANNEL_ID, OC_CHANNEL_ID, OC_FORECAST_MONTH_DAY, MOD_ROLE_ID, PLAYER_LIST_PASSWORD

import socket
from datetime import date

class Stats(commands.Cog):

    def __init__(self, dictator: commands.Bot) -> None:
        self.dictator = dictator

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        if await self.prepare_stats():
            self.stats_loop.start()    
            self.open_collective_forecast.start()         

    @tasks.loop(minutes=1)
    async def stats_loop(self) -> None:
        await self.update_stats()

    async def update_stats(self) -> None:
        pl = await self.player_list_request()
        await self.verify_player_list(pl)
        server_info, player_list = await self.parse_player_list(pl)

        embed = discord.Embed(title="Stats", colour=0xffbb35)
        embed.add_field(name="Online", value=server_info[0])
        embed.add_field(name="Version", value=server_info[1])
        embed.add_field(name="Players", value=player_list[0:5], inline=False)
        await self.stats_message.edit(embed=embed)
        
    async def prepare_stats(self) -> bool:
        channel = self.dictator.get_channel(STATS_CHANNEL_ID)

        if channel is None:
            print("Unable to find channel, disabling stats extension.")
            await self.dictator.unload_extension("cogs.stats")
            return False

        async for msg in channel.history(limit=2):
            if msg.author == self.dictator.user:
                await msg.delete()

        embed = discord.Embed(title="Loading stats...", colour=0xffbb35)
        self.stats_message = await channel.send(embed=embed)
        return True

    async def get_population(self) -> str:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            sock.settimeout(3.0)
            sock.connect(("play.twohoursonelife.com", 8005))
            fd = sock.makefile()

        except ConnectionRefusedError:
            app_info = await self.dictator.application_info()
            owner = await self.dictator.fetch_user(app_info.team.owner_id)
            await owner.send("Is the game server offline? it did not respond to a stats request.")
            print("Server failed stats request, pinged my owner.")
            return "Unknown"

        else:
            if "SN" in fd.readline(128):
                count = fd.readline(128).split("/")
                return f"{count[0]}"

        finally:
            sock.close()

    async def player_list_request(self) -> str:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2)
            s.connect(("play.twohoursonelife.com", 8005))
            if PLAYER_LIST_PASSWORD:
                s.sendall(f"PLAYER_LIST {PLAYER_LIST_PASSWORD}#".encode("utf-8"))
            else:
                s.sendall(f"PLAYER_LIST#".encode("utf-8")) # format changes if no password

            data_bytes = []
            messages_received = 0
            while True:
                try:
                    chunk = s.recv(1024)
                
                except TimeoutError:
                    break
                
                else:
                    if not chunk or chunk == b"":
                        break # sudden disconnect
                    data_bytes.append(chunk)
                    messages_received += chunk.count(ord('#'))
                    if messages_received >= 2: # SN and PLAYER_LIST
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
        
        return player_list[:3], player_list[3:]

    async def open_collective_forecast_embed(self) -> discord.Embed:
        forecast = ForecastOpenCollective.forecast()
        description = (
            f"**TLDR:** Sufficient funding until **{forecast['forecast_continued_income']}**"
            f"\n\n**Details:** Assuming expenses remain similar and:"
            f"\n- assuming we receive **no future income**, we have funding until **{forecast['forecast_no_income']}**"
            f"\n- assuming **average donations continue**, we have funding until **{forecast['forecast_continued_income']}**"
            f"\n\n**Current balance: {forecast['current_balance']}**"
            f"\n\n*\*Data time period: past {forecast['analysis_period_months']} months. This is only a forecast and is likely to change. Forecast is up to a max of 5 years.*"
        )
        
        return discord.Embed(title="Summary of 2HOL Open Collective finances:", description=description, colour=0x37ff77)

    @tasks.loop(hours=24)
    async def open_collective_forecast(self) -> None:
        if date.today().day != OC_FORECAST_MONTH_DAY:
            return
        
        channel = self.dictator.get_channel(OC_CHANNEL_ID)
        embed = await self.open_collective_forecast_embed()
        await channel.send(embed=embed)

    @app_commands.checks.has_role(MOD_ROLE_ID)
    @app_commands.command()
    async def open_collective(self, interaction: discord.Interaction) -> None:
        """Generates and sends Open Collective forecast to the current channel."""
        await interaction.response.defer()
        
        embed = await self.open_collective_forecast_embed()
        await interaction.followup.send(embed=embed)


async def setup(dictator: commands.Bot) -> None:
    await dictator.add_cog(Stats(dictator))
