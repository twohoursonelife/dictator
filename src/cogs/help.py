import discord
from discord.ext import commands


class Help(commands.Cog):

    def __init__(self, dictator):
        self.dictator = dictator
        self.dictator.remove_command('help')

    @commands.command(pass_context=True)
    async def help(self, ctx):
        channel = ctx.message.channel
        descrip = '**-status** - Displays number of online players'
        descrip += '\n**-online** - Displays number of online players'
        descrip += '\n**-key** - Sends DM with player login info'
        embed = discord.Embed(
            title='Commands list:',
            description=descrip,
            colour=discord.Colour.red()
        )
        await channel.send(embed=embed)


def setup(dictator):
    dictator.add_cog(Help(dictator))
