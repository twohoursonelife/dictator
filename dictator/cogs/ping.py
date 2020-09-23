from discord.ext import commands


class Ping(commands.Cog):

    def __init__(self, dictator):
        self.dictator = dictator

    @commands.command(brief='Check the bot\'s latency.', help='Check the bot\'s latency or whether it\'s responding at all.')
    async def ping(self, ctx):
        await ctx.send(f'Pong! That took me {round(self.dictator.latency * 1000)}ms!')


def setup(dictator):
    dictator.add_cog(Ping(dictator))
