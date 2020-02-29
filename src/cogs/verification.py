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
    async def on_raw_reaction_add(self, event):
        global checkVerification
        global verificationMSGID

        channel = self.dictator.get_channel(int(config.read('verify_channel_id')))
        member = channel.guild.get_member(event.user_id)
        message = await channel.fetch_message(verificationMSGID)
        emoji = event.emoji.name

        if event.message_id == verificationMSGID and checkVerification and member.id != int(config.read('bot_id')):
            
            #Need to find a way to get the specific reaction and remove it using raw payload data
            #await reaction.remove(user)
            await message.remove_reaction(emoji, member)
            if emoji == '✅':
                role = get(channel.guild.roles, name='Verified')
                await member.add_roles(role, reason='User successfully verified.')
                # Finally, create a game account for the user
                await self.dictator.get_cog('User').create_user(member)

            elif emoji == '❌':
                try:
                    invite = await channel.create_invite(max_uses=1, reason=f'Sent to {member.name}{member.discriminator}, user kicked after did not agree to rules')
                    await member.send(f'Sorry to see you go!\nIf you change your mind, you can use this link to jump back in.\n{invite}')
                
                except:
                    print(f'Unable to message {member.name}#{member.discriminator} an invite after they failed verification.')
                
                try:                    
                    await channel.guild.kick(member, reason='User did not accept the rules.')
                
                except discord.Forbidden as e:
                    await member.send(f'Where do you think you\'re going, {member.mention}?\nYour soul is bound to 2HOL, remember?')
                    print(f'{member} tried to escape, but failed miserably.')

                else:
                    print(f'{member.name}#{member.discriminator} failed verification and has been kicked from the discord.')


def setup(dictator):
    dictator.add_cog(Verification(dictator))
