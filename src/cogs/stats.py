import discord
import socket
from discord.ext import commands, tasks
import config_manager as config


class Stats(commands.Cog):

    def __init__(self, dictator):
        self.dictator = dictator

    @commands.Cog.listener()
    async def on_ready(self):
        self.channel = self.dictator.get_channel(int(config.read('general_channel_id')))

        if self.channel is None:
            print('Unable to find channel, disabling stats extension.')
            self.dictator.unload_extension('cogs.stats')
            return

        #async for message in self.channel.history(limit=1):
            #await message.delete()

        #embed = discord.Embed(title='Loading stats...', colour=0xffbb35)
        #self.message = await self.channel.send(embed=embed)
        await self.channel.edit(reason='Update player count', topic='Players in game: Loading...')

        self.stats.start()

    @tasks.loop(minutes=5)
    async def stats(self):
        online = await self.get_population()

        #embed = discord.Embed(title='Stats', colour=0xffbb35)
        #embed.add_field(name='In game:', value=f'{online}')
        #await self.message.edit(embed=embed)
        await self.channel.edit(reason='Update player count', topic=f'Players in game: {online}')

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
