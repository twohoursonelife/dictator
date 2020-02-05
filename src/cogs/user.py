import discord
import mysql.connector
from discord.ext import commands


class User(commands.Cog):

    def __init__(self, dictator):
        self.dictator = dictator

    async def createKey(parameter_list):
        pass

    # Retrieve existing users information
    @commands.command()
    async def key(self, ctx):
        await ctx.author.send(f'Hey {ctx.author.mention}! Here is your login information:\n\n**Username:** USERNAME\n**Key:** KEY')
        await ctx.send(f'{ctx.author.mention} I\'ve sent you a message with your login information.')
        


def setup(dictator):
    dictator.add_cog(User(dictator))
