import discord
from discord.ext import commands
from discord.utils import get

checkVerification = True
verificationMSGID = 0


class Verification(commands.Cog):

    def __init__(self, dictator):
        self.dictator = dictator

    @commands.Cog.listener()
    async def on_ready(self):

        await self.verification()

    async def verification(self):

        # This needs to be in a config
        # This is the verification channel
        channel = self.dictator.get_channel(660359992410636288)

        # Delete message history
        async for message in channel.history(limit=10):
            await message.delete()

        # These messages should be in a config file
        await channel.send(file=discord.File('media/2HOL-600px.png'))
        verifyMessage = await channel.send('Welcome to 2HOL!\nTo join our community, you must agree to the #rules\nThese rules can be changed at any time, but we\'ll be sure to tell you this in #notices\n\nTo tell use that you accept and will follow our rules react to this message with ✅\nIf you do not accept these rules, react to this message with ❌')

        global verificationMSGID
        verificationMSGID = verifyMessage.id

        await verifyMessage.add_reaction('✅')
        await verifyMessage.add_reaction('❌')

    # Activates when a user has reacted to verification message and processes the user.
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        global checkVerification
        global verificationMSGID

        # ID of bot should be in a config file
        if reaction.message.id == verificationMSGID and checkVerification and user.id != 658883039761399859:
            await reaction.remove(user)
            if reaction.emoji == '✅':
                role = get(user.guild.roles, name='Verified')
                await user.add_roles(role, reason='User agreed to rules')
                await user.send(content=f'Hey {user.name},\nGreat to have you here!\n**I\'ll be sending you some information soon so you can log in and play the game.**\n\nIf you have any trouble downloading, setting up or joining the game please ask for help\nin our help channel and wait patiently for someone to come to your rescue!')

            elif reaction.emoji == '❌':
                invite = await reaction.message.channel.create_invite(max_uses=1, reason=f'Sent to {user.name}{user.discriminator}, user kicked after did not agree to rules')
                await user.send(content=f'Sorry to see you go!\nIf you change your mind, you can use this link to jump back in.\n{invite}')
                await reaction.message.guild.kick(user, reason='User did not accept the rules.')


def setup(dictator):
    dictator.add_cog(Verification(dictator))
