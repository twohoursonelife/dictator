import discord
from discord.ext import commands

class Verification(commands.Cog):

    def __init__(self, dictator):
        self.dictator = dictator

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await self.dictator.get_cog('User').create_user(member)

def setup(dictator):
    dictator.add_cog(Verification(dictator))
