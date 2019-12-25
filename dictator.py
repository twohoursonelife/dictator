import discord
from discord.ext import commands, tasks
from itertools import cycle

# Ensure to create a token.txt file in the same directory as this file which contains only the token of the bot.

dictator = commands.Bot(command_prefix='-')
status = cycle(['Dictatorship', f'{dictator.command_prefix}help', 'Bullying Colin', 'Griefing Newport', 'Praising Sam'])

@dictator.event
async def on_ready():
    print('The 2HOL Dictator has risen!')
    changeStatus.start()
    

@tasks.loop(seconds=10)
async def changeStatus():
    await dictator.change_presence(activity=discord.Game(next(status)))

@dictator.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f'Invalid command. See {prefix}help')

@dictator.command()
async def ping (ctx):
    await ctx.send(f'Pong! {round(dictator.latency * 1000)}ms')

token = open('token.txt', 'r')
dictator.run(token.readline())
token.close