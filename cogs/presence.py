import discord
from discord.ext import commands, tasks
from itertools import cycle


class Presence(commands.Cog):

    def __init__(self, dictator):
        self.dictator = dictator

    @commands.Cog.listener()
    async def on_ready(self):

        self.change_status.start()

    @tasks.loop(seconds=10)
    async def change_status(self):

        # Value should be in a config
        status = cycle(['Dictatorship', '-help', 'Bullying Colin', 'Guarding Newport',
                        'Praising Sam', 'Baking the pies', 'Cheesing Uno', 'Hidei ho ho ho'])

        await self.dictator.change_presence(activity=discord.Game(next(status)))


def setup(dictator):
    dictator.add_cog(Presence(dictator))
