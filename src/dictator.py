import discord
import os
import yaml
from discord.ext import commands

# These values should be in a config file
prefix = '-'
dictator = commands.Bot(command_prefix=prefix)


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

# Loading of all cog files in the cogs directory
for filename in os.listdir(f'src/cogs'):
    if filename.endswith('.py'):
        dictator.load_extension(f'cogs.{filename[:-3]}')

# Load config

# Ensure to create a token.txt file in the same directory as this file which contains only the token of the bot.
token = open('src/token.txt', 'r')
dictator.run(token.readline())
token.close
