import discord
from discord.ext import commands


class Informational(commands.Cog):

    def __init__(self, dictator):
        self.dictator = dictator

    @commands.command(brief='Read the \'fricken\' manual.', help='Sends basic infoamtion about playing for the first time.')
    async def rtfm(self, ctx):
        await ctx.message.delete()
        await ctx.send(f'Heres the manual to play for the first time\n<https://twohoursonelife.com/first-time-playing>\n\nCheck your messages from me to find your username and password.')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.content == '.key' or message.content == '.mykey':
            await message.delete()
            await message.channel.send(f'{message.author.mention} You need to use `-key`', delete_after=10)


def setup(dictator):
    dictator.add_cog(Informational(dictator))
