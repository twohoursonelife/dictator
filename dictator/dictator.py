import discord
import os
from discord.ext import commands
import config_manager as config

print(config.check_config())

dictator = commands.Bot(command_prefix=config.read('bot_prefix'), case_insensitive=True)

@dictator.event
async def on_ready():
    print('The 2HOL Dictator has risen!')

# Loading of all cog files in the cogs directory
for filename in os.listdir('dictator/cogs'):
    if filename.endswith('.py'):
        dictator.load_extension(f'cogs.{filename[:-3]}')


dictator.run(config.read('bot_token'))
