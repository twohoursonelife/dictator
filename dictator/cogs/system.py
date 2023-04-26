from discord.ext import commands
from discord.ext.commands import Context
import random

class System(commands.Cog):

    def __init__(self, dictator):
        self.dictator = dictator

    @commands.command(brief='Check the bot\'s latency.', help='Check the bot\'s latency or whether it\'s responding at all.')
    async def ping(self, ctx):
        if random.randint(1, 100) == 1:
            await ctx.send(f'Stop that, it hurts ;(')
        else:
            await ctx.send(f'Pong! That took me {round(self.dictator.latency * 1000)}ms!')
            
    @commands.command(brief='Replies with Dictators\'s current version.', help='Check the bot\'s version.')
    async def version(self, ctx):
        with open('version.txt', 'r') as file:
            await ctx.send(file.read())
            
    @commands.command(brief='Sync Dictators app commands to the current guild.')
    @commands.guild_only()
    @commands.is_owner()
    async def sync(self, ctx: Context) -> None:
        synced = await ctx.bot.tree.sync(guild=ctx.guild)
        await ctx.send(f'Synced `{len(synced)}` commands to the current guild.')


async def setup(dictator):
    await dictator.add_cog(System(dictator))
