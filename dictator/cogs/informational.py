import discord
from discord.ext import commands


class Informational(commands.Cog):

    def __init__(self, dictator):
        self.dictator = dictator

    @commands.command(brief='Read the \'fricken\' manual.', help='Sends basic infoamtion about playing for the first time.')
    async def rtfm(self, ctx):
        await ctx.send(f'**Heres the manual to play for the first time**\n<https://twohoursonelife.com/first-time-playing>\n\nCheck your messages from me to find your username and password.')


def setup(dictator):
    dictator.add_cog(Informational(dictator))
