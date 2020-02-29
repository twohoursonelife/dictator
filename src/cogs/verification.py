import discord
from discord.ext import commands
from discord.utils import get
import config_manager as config

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
        verifyMessage = await channel.send('Welcome to 2HOL!\nTo join our community, you must agree to the #rules\nThese rules can be changed at any time, but we\'ll be sure to tell you this in #notices\n\nTo tell us that you accept and will follow our rules react to this message with ✅')

        global verificationMSGID
        verificationMSGID = verifyMessage.id

        await verifyMessage.add_reaction('✅')

    # Activates when a user has reacted to verification message and processes the user.
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, event):
        global verificationMSGID

        channel = self.dictator.get_channel(int(config.read('verify_channel_id')))
        member = channel.guild.get_member(event.user_id)
        message = await channel.fetch_message(verificationMSGID)
        emoji = event.emoji.name

        if event.message_id == verificationMSGID and member.id != int(config.read('bot_id')):
            await message.remove_reaction(emoji, member)
            if emoji == '✅':
                role = get(channel.guild.roles, name='Verified')
                await member.add_roles(role, reason='User successfully verified.')
                # Finally, create a game account for the user
                await self.dictator.get_cog('User').create_user(member)


def setup(dictator):
    dictator.add_cog(Verification(dictator))
