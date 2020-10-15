import os
from discord.ext import commands
import utility.config_manager as config
import discord


print(config.check_config())

intents = discord.Intents.all()

dictator = commands.Bot(command_prefix=config.read('bot_prefix'), case_insensitive=True, intents=intents)

@dictator.event
async def on_ready():
    print('The 2HOL Dictator has risen!')

# Loading of all cog files in the cogs directory
for filename in os.listdir('dictator/cogs'):
    if filename.endswith('.py'):
        dictator.load_extension(f'cogs.{filename[:-3]}')


dictator.run(config.read('bot_token'))
