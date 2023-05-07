import discord

from discord.ext import commands, tasks

from open_collective import ForecastOpenCollective
from constants import STATS_CHANNEL_ID, OC_CHANNEL_ID, OC_FORECAST_MONTH_DAY

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
        online = await self.get_population()

        embed = discord.Embed(title="Server statistics:", colour=0xffbb35)
        embed.add_field(name="Players online:", value=online)
        await self.stats_message.edit(embed=embed)
        
    async def prepare_stats(self) -> bool:
        channel = self.dictator.get_channel(STATS_CHANNEL_ID)

        if channel is None:
            print("Unable to find channel, disabling stats extension.")
            await self.dictator.unload_extension("cogs.stats")
            return False

        async for msg in channel.history(limit=3):
            await msg.delete()

        embed = discord.Embed(title="Loading Server statistics...", colour=0xffbb35)
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

    async def send_open_collective_forecast_embed(self, channel: discord.TextChannel) -> None:
        forecast = ForecastOpenCollective.forecast()
        description = (
            f"**TLDR:** Sufficient funding until **{forecast['forecast_continued_income']}**"
            f"\n\n**Details:** Assuming expenses remain similar and:"
            f"\n- assuming we receive **no future income**, we have funding until **{forecast['forecast_no_income']}**"
            f"\n- assuming **average donations continue**, we have funding until **{forecast['forecast_continued_income']}**"
            f"\n\n**Current balance: {forecast['current_balance']}**"
            f"\n\n*\*Data time period: past {forecast['analysis_period_months']} months. This is only a forecast and is likely to change. Forecast is up to a max of 5 years.*"
        )
        embed = discord.Embed(title="Summary of 2HOL Open Collective finances:", description=description, colour=0x37ff77)
        await channel.send(embed=embed)

    @tasks.loop(hours=24)
    async def open_collective_forecast(self) -> None:
        if date.today().day != OC_FORECAST_MONTH_DAY:
            return
        
        channel = self.dictator.get_channel(OC_CHANNEL_ID)
        await self.send_open_collective_forecast_embed(channel)


    @commands.command(aliases=["oc"], brief="Generates and sends Open Collective forecast to the current channel.")
    @commands.has_any_role("Discord mod")
    async def open_collective(self, ctx: commands.Context) -> None:
        await ctx.message.delete()
        await self.send_open_collective_forecast_embed(ctx.channel)


async def setup(dictator: commands.Bot) -> None:
    await dictator.add_cog(Stats(dictator))
