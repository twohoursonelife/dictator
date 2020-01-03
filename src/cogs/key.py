import discord
from discord.ext import commands


class Key(commands.Cog):

    def __init__(self, dictator):
        self.dictator = dictator

    async def createKey(parameter_list):
        pass


def setup(dictator):
    dictator.add_cog(Key(dictator))
