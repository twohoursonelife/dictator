import discord
import os
import yaml
from discord.ext import commands

# Load config
with open('src/conf.yaml', 'r') as file:
    global conf
    conf = yaml.load(file, Loader=yaml.FullLoader)

# Use prefix as variable for f string compatability
prefix = conf['prefix']

# Create bot
dictator = commands.Bot(command_prefix=conf['prefix'])

# Ensure to create a token.txt file in the same directory as this file which contains only the token of the bot.
# Reads token of bot
with open('src/token.txt', 'r') as file:
    dictator.run(file.readline())

# Loading of all cog files in the cogs directory
for filename in os.listdir(f'src/cogs'):
    if filename.endswith('.py'):
        dictator.load_extension(f'cogs.{filename[:-3]}')

@dictator.event
async def on_ready():

    print('The 2HOL Dictator has risen!')

# Global error handling
@dictator.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f'Invalid command. See {prefix}help')
        return

    if isinstance(error, commands.MissingPermissions):
        await ctx.send('Insufficient permissions')
        return

    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'Missing argument. See {prefix}help')
        return

    print(error)
