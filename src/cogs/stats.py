import discord
import socket
from discord.ext import commands, tasks
import config_manager as config


class Stats(commands.Cog):

    def __init__(self, dictator):
        self.dictator = dictator

    @commands.Cog.listener()
    async def on_ready(self):
        self.channel = self.dictator.get_channel(
            int(config.read('general_channel_id')))

        if self.channel is None:
            print('Unable to find channel, disabling stats extension.')
            self.dictator.unload_extension('cogs.stats')
            return

        await self.channel.edit(reason='Update statistics', topic='Loading stats...')

        self.stats_loop.start()

    @tasks.loop(minutes=15)
    async def stats_loop(self):
        await self.update_stats()

    @commands.command(aliases=['online', 'status'], brief='Updates stats in #general channel description.', help='Updates stats in #general channel description. Replaces online/status command.')
    async def stats(self, ctx):
        await ctx.message.delete()
        await self.update_stats()
        embed = discord.Embed(title='I\'ve update the stats in the #general channel description.', description='They otherwise update every 15 minutes.', colour=0xffbb35)
        await ctx.send(embed=embed, delete_after=5)

    async def update_stats(self):
        online = await self.get_population()

        await self.channel.edit(reason='Update statistics', topic=f'Players in game: {online}')
        print(f'Stats updated: Players in game: {online}')

    async def get_population(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            sock.connect(('play.twohoursonelife.com', 8005))
            fd = sock.makefile()

        except:
            return 'Unknown'

        else:
            if 'SN' in fd.readline(128):
                count = fd.readline(128).split('/')
                return f'{count[0]}'

        finally:
            sock.close()


def setup(dictator):
    dictator.add_cog(Stats(dictator))
