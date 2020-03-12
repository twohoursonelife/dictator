import discord
from discord.ext import commands, tasks
from itertools import cycle


class Presence(commands.Cog):

    def __init__(self, dictator):

        self.dictator = dictator

        self.status = cycle(['Dictatorship', '-help', 'Bullying Colin', 'Guarding Newport',
                             'Praising Sam', 'Baking the pies', 'Cheesing Uno', 'Hidei ho ho ho', 'Celebrating Two Years'])

    @commands.Cog.listener()
    async def on_ready(self):

        self.change_status.start()

    @tasks.loop(seconds=10)
    async def change_status(self):

        await self.dictator.change_presence(activity=discord.Game(next(self.status)))


def setup(dictator):
    dictator.add_cog(Presence(dictator))
