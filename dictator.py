import discord
from discord.ext import commands, tasks
from itertools import cycle

# Ensure to create a token.txt file in the same directory as this file which contains only the token of the bot.

prefix = '-'
dictator = commands.Bot(command_prefix=prefix)
status = cycle(['Dictatorship', f'{prefix}help', 'Bullying Colin',
                'Guarding Newport', 'Praising Sam', 'Resetting Amanis score', 'Baking the pies'])


@dictator.event
async def on_ready():
    print('The 2HOL Dictator has risen!')
    change_status.start()


@tasks.loop(seconds=10)
async def change_status():
    await dictator.change_presence(activity=discord.Game(next(status)))


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


@dictator.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round(dictator.latency * 1000)}ms')

token = open('token.txt', 'r')
dictator.run(token.readline())
token.close
