from discord.ext import commands
import random

class Ping(commands.Cog):

    def __init__(self, dictator):
        self.dictator = dictator

    @commands.command(brief='Check the bot\'s latency.', help='Check the bot\'s latency or whether it\'s responding at all.')
    async def ping(self, ctx):
        if random.randint(1, 100) == 1:
            await ctx.send(f'Stop that, it hurts ;(')
        else:
            await ctx.send(f'Pong! That took me {round(self.dictator.latency * 1000)}ms!')


async def setup(dictator):
    await dictator.add_cog(Ping(dictator))
