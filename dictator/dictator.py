import os
from discord.ext import commands
import discord
from constants import BOT_PREFIX, BOT_TOKEN


intents = discord.Intents.all()

dictator = commands.Bot(command_prefix=BOT_PREFIX, case_insensitive=True, intents=intents)

@dictator.event
async def on_ready():
    print('The 2HOL Dictator has risen!')

# Loading of all cog files in the cogs directory
for filename in os.listdir('dictator/cogs'):
    if filename.endswith('.py'):
        dictator.load_extension(f'cogs.{filename[:-3]}')


dictator.run(BOT_TOKEN)
