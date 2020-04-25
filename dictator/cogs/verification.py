import discord
from discord.ext import commands
from discord.utils import get
import utility.config_manager as config

verificationMSGID = 0


class Verification(commands.Cog):

    def __init__(self, dictator):
        self.dictator = dictator

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        # We're only interested if theres been a change to a users roles
        if before.roles != after.roles:
            role = get(before.guild.roles, name='Unverified')
            # User had unverfied role before, afterwards they do not have the unverified role
            if role in before.roles and role not in after.roles:
               # Create game account for the member
               await self.dictator.get_cog('User').create_user(after)

def setup(dictator):
    dictator.add_cog(Verification(dictator))
