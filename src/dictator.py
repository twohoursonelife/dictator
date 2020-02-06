import discord
import os
from discord.ext import commands
import config_manager as config

print(config.check_config())

dictator = commands.Bot(command_prefix=config.read('bot_prefix'))

@dictator.event
async def on_ready():
    print('The 2HOL Dictator has risen!')

# Global error handling
@dictator.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f'Invalid command. See {dictator.get_prefix}help')

    elif isinstance(error, commands.MissingPermissions):
        await ctx.send('Insufficient permissions')

    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'Missing argument. See {dictator.get_prefix}help')

    elif isinstance(error, commands.NoPrivateMessage):
        await ctx.send(f'{ctx.author.mention}, you can\'t use this command in a private message. Head to the bot channel.')

    else:
        await ctx.send(f'Uh oh... {ctx.guild.owner.mention} broke something again. Stand by.')
        print(f'\n\nCOMMAND ERROR:\nAuthor: {ctx.author}\nChannel: {ctx.channel}\nCommand: {ctx.message.content}\n{error}\n\n')

# Loading of all cog files in the cogs directory
for filename in os.listdir('src/cogs'):
    if filename.endswith('.py'):
        dictator.load_extension(f'cogs.{filename[:-3]}')

# Ensure the bot's token is stored in token.txt for the bot to work
#with open('src/token.txt', 'r') as file:
 #   dictator.run(file.readline())
dictator.run(config.read('bot_token'))
