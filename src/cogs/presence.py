import discord
import yaml
from discord.ext import commands, tasks
from itertools import cycle


class Presence(commands.Cog):

    def __init__(self, dictator):

        self.dictator = dictator

        # Load config
        with open('src/conf.yaml', 'r') as file:
            conf = yaml.load(file, Loader=yaml.FullLoader)

        # Use prefix as variable for f string compatability
        prefix = conf['prefix']

        # Value should be in a config
        self.status = cycle(['Dictatorship', f'{prefix}help', 'Bullying Colin', 'Guarding Newport',
                             'Praising Sam', 'Baking the pies', 'Cheesing Uno', 'Hidei ho ho ho'])

    @commands.Cog.listener()
    async def on_ready(self):

        self.change_status.start()

    @tasks.loop(seconds=10)
    async def change_status(self):

        await self.dictator.change_presence(activity=discord.Game(next(self.status)))


def setup(dictator):
    dictator.add_cog(Presence(dictator))
