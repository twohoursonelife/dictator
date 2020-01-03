import discord
import os
from discord.ext import commands

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
for filename in os.listdir('src/cogs'):
    if filename.endswith('.py'):
        dictator.load_extension(f'cogs.{filename[:-3]}')

# Ensure the bot's token is stored in token.txt for the bot to work
with open('src/token.txt', 'r') as file:
    dictator.run(file.readline())
