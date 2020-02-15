import discord
from discord.ext import commands
from discord.utils import get
import config_manager as config

# Do we enable user verification?
checkVerification = bool(config.read('verify_discord_users'))

verificationMSGID = 0


class Verification(commands.Cog):

    def __init__(self, dictator):
        self.dictator = dictator

    @commands.Cog.listener()
    async def on_ready(self):

        await self.verification()

    async def verification(self):

        # This is the verification channel
        channel = self.dictator.get_channel(int(config.read('verify_channel_id')))

        # Delete message history
        async for message in channel.history(limit=10):
            await message.delete()

        # These messages should be in a config file
        await channel.send(file=discord.File('src/media/2HOL-600px.png'))
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

        if reaction.message.id == verificationMSGID and checkVerification and user.id != int(config.read('bot_id')):
            await reaction.remove(user)
            if reaction.emoji == '✅':
                role = get(user.guild.roles, name='Verified')
                await user.add_roles(role, reason='User agreed to rules')
                await user.send(content=f'Hey {user.mention},\nGreat to have you here!\nI\'ll send you some information soon so you can play the game.')
                # Finally, create a game account for the user
                await self.dictator.get_cog('User').create_user(user)

            elif reaction.emoji == '❌':
                try:
                    invite = await reaction.message.channel.create_invite(max_uses=1, reason=f'Sent to {user.name}{user.discriminator}, user kicked after did not agree to rules')
                    await user.send(f'Sorry to see you go!\nIf you change your mind, you can use this link to jump back in.\n{invite}')
                
                except:
                    print(f'Unable to message {user.name}#{user.discriminator} an invite after they failed verification.')
                
                try:                    
                    await reaction.message.guild.kick(user, reason='User did not accept the rules.')
                
                except discord.Forbidden as e:
                    await user.send(f'Where do you think you\'re going, {user.mention}?\nYour soul is bound to 2HOL, remember?')
                    print(f'{user} tried to escape, but failed miserably.')


def setup(dictator):
    dictator.add_cog(Verification(dictator))
