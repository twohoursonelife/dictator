import discord
from discord.ext import commands

# Ensure to create a token.txt file in the same directory as this file which contains only the token of the bot.

dictator = commands.Bot(command_prefix='-')

@dictator.event
async def on_ready():
    print('The 2HOL Dictator has risen!')

@dictator.command()
async def ping (ctx):
    await ctx.send(f'Pong! {round(dictator.latency * 1000)}ms')

token = open('token.txt', 'r')
dictator.run(token.readline())
token.close