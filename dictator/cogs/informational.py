import discord
from discord.ext import commands


class Informational(commands.Cog):

    def __init__(self, dictator):
        self.dictator = dictator

    @commands.command(aliases=['firstinfo', 'readyourfrickenmessages', 'readyourfuckingmessages'], brief='Help information about playing for the first time.', help='Send the help information about playing for the first time, made especially for those who ignore it already sent to them from the bot.')
    async def ryfm(self, ctx):
        await ctx.send(f'**How to join the game for the first time.**\nRead all about it here <https://twohoursonelife.com/first-time-playing>\n\nCheck your messages from me to find your username and password.')


def setup(dictator):
    dictator.add_cog(Informational(dictator))
