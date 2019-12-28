import discord
from discord.ext import commands, tasks
from itertools import cycle

# Ensure to create a token.txt file in the same directory as this file which contains only the token of the bot.

prefix = '-'
checkVerification = False
verificationMSGID = 0
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


@dictator.command()
async def ping(ctx):
    await ctx.send(f'Pong! {round(dictator.latency * 1000)}ms')


@dictator.command()
@commands.has_role('Leader')
async def a(ctx):
    # Must delete previous messages in channel

    await ctx.message.delete()

    channel = dictator.get_channel(648080619146051623)
    await channel.send(file=discord.File('img/2HOL-600px.png'))
    verifyMessage = await channel.send('Welcome to 2HOL.\nTo join our community, you must agree to the #rules\nThese rules can be adjusted at any time, you will be notified of this in #notices\n\nTo confirm you have read and agreed to our rules please type `!verify`')

    global verificationMSGID
    verificationMSGID = verifyMessage.id

    global checkVerification
    checkVerification = True

    await verifyMessage.add_reaction('✅')
    await verifyMessage.add_reaction('❌')

# Need a check so we dont verify or kick this bot
@dictator.event
async def on_raw_reaction_add(reaction):
    global checkVerification
    global verificationMSGID

    if reaction.message_id == verificationMSGID and checkVerification:
        if reaction.emoji.name == '✅':
            print('User verified')
            # verify user
        elif reaction.emoji.name == '❌':
            print('User kicked')
            # Kick user and send them message with join link
        else:
            print('invalid reaction')
            print(reaction)
            # remove reaction


token = open('token.txt', 'r')
dictator.run(token.readline())
token.close
