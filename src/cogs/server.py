import discord
import socket
from discord.ext import commands

class Server(commands.Cog):

    def __init__(self, dictator):
        self.dictator = dictator

    @commands.command(aliases=['status'])
    async def online(self, ctx):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            sock.connect(('play.twohoursonelife.com', 8005))
            fd = sock.makefile()

        except:
            embed = discord.Embed(title='Failed to check players online', description='Is the server offline?')
            await ctx.send(embed=embed)

        else:
            if 'SN' in fd.readline(128):
                count = fd.readline(128).split('/')
                if int(count[0]) == 1:
                    embed = discord.Embed(title='1 player is online', colour=0xffbb35)
                else:
                    embed = discord.Embed(title=f'{count[0]} players are online', colour=0xffbb35)
                
                await ctx.send(embed=embed)

        finally:
            sock.close()


def setup(dictator):
    dictator.add_cog(Server(dictator))
