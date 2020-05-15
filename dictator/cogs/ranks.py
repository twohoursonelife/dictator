import discord
from discord.ext import commands
from utility.db_manager import db_connection as db_conn


class Ranks(commands.Cog):

    def __init__(self, dictator):
        self.dictator = dictator

    @commands.command(brief='Claim the \'Experienced Player\' rank.', help='If you have 50 or more hours in game, you can claim this special rank.')
    async def exp(self, ctx):
        pass


def setup(dictator):
    dictator.add_cog(Ranks(dictator))
