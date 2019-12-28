import discord
from discord.ext import commands, tasks
from itertools import cycle

# Ensure to create a token.txt file in the same directory as this file which contains only the token of the bot.

# These values should be in a config file
prefix = '-'
checkVerification = True
verificationMSGID = 0
dictator = commands.Bot(command_prefix=prefix)
status = cycle(['Dictatorship', f'{prefix}help', 'Bullying Colin',
                'Guarding Newport', 'Praising Sam', 'Baking the pies', 'Cheesing Uno'])


@dictator.event
async def on_ready():

    print('The 2HOL Dictator has risen!')

    change_status.start()

    await verification()


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


async def verification():

    # This needs to be in a config
    # This is the verification channel
    channel = dictator.get_channel(660359992410636288)

    # Delete message history
    async for message in channel.history(limit=10):
        await message.delete()

    # These messages should be in a config file
    await channel.send(file=discord.File('img/2HOL-600px.png'))
    verifyMessage = await channel.send('Welcome to 2HOL!\nTo join our community, you must agree to the #rules\nThese rules can be changed at any time, but we\'ll be sure to tell you this in #notices\n\nTo tell use that you accept and will follow our rules react to this message with ✅\nIf you do not accept these rules, react to this message with ❌')

    global verificationMSGID
    verificationMSGID = verifyMessage.id

    await verifyMessage.add_reaction('✅')
    await verifyMessage.add_reaction('❌')

# Activates when a user has reacted to verification message and processes the user.
@dictator.event
async def on_reaction_add(reaction, user):
    global checkVerification
    global verificationMSGID

    # ID of bot should be in a config file
    if reaction.message.id == verificationMSGID and checkVerification and user.id != 658883039761399859:
        
        if reaction.emoji == '✅':
            await reaction.remove(user)
            role = get(user.guild.roles, name='Verified')
            await user.add_roles(role, reason='User agreed to rules')

        elif reaction.emoji == '❌':
            await reaction.remove(user)
            invite = await reaction.message.channel.create_invite(max_uses=1, reason=f'Sent to {user.name}{user.discriminator}, user kicked after did not agree to rules')
            await user.send(content=f'Sorry to see you go!\nIf you change your mind, you can use this link to jump back in.\n{invite}')
            await reaction.message.guild.kick(user, reason='You did not accept the rules.')

        else:
            await reaction.remove(user)


token = open('token.txt', 'r')
dictator.run(token.readline())
token.close
