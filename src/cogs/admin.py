import discord
from discord.ext import commands


class Admin(commands.Cog):

    def __init__(self, dictator):
        self.dictator = dictator

def setup(dictator):
    dictator.add_cog(Admin(dictator))
