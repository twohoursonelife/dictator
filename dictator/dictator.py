import os
from discord.ext import commands
import discord
from constants import BOT_PREFIX, BOT_TOKEN


class Dictator(commands.Bot):
    async def setup_hook(self) -> None:
        for filename in os.listdir("dictator/cogs"):
            if filename.endswith(".py"):
                await dictator.load_extension(f"cogs.{filename[:-3]}")


intents = discord.Intents.all()
dictator = Dictator(command_prefix=BOT_PREFIX, case_insensitive=True, intents=intents)


@dictator.event
async def on_ready() -> None:
    print("The 2HOL Dictator has risen!")


dictator.run(BOT_TOKEN)
