import discord
import socket
from discord.ext import commands, tasks
from constants import STATS_CHANNEL_ID
from datetime import date
from dateutil.relativedelta import relativedelta


class Stats(commands.Cog):

    def __init__(self, dictator):
        self.dictator = dictator

    @commands.Cog.listener()
    async def on_ready(self):
        self.channel = self.dictator.get_channel(STATS_CHANNEL_ID)

        if self.channel is None:
            print('Unable to find channel, disabling stats extension.')
            self.dictator.unload_extension('cogs.stats')
            return

        async for msg in self.channel.history(limit=3):
            await msg.delete()

        embed = discord.Embed(title='Loading Server statistics...', colour=0xffbb35)
        self.stats_msg = await self.channel.send(embed=embed)

        if not self.stats_loop.is_running():
            self.stats_loop.start()            

    @tasks.loop(minutes=1)
    async def stats_loop(self):
        await self.update_stats()

    async def update_stats(self):
        online = await self.get_population()

        embed = discord.Embed(title='Server statistics:', colour=0xffbb35)
        embed.add_field(name='Players online:', value=online)
        await self.stats_msg.edit(embed=embed)

        '''
        # "Temp" player count logging
        with open('dictator/utility/player-log.txt', 'a') as f:
            f.write(f'{online} - {datetime.datetime.now()}\n')
        '''

    async def get_population(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            sock.settimeout(3.0)
            sock.connect(('play.twohoursonelife.com', 8005))
            fd = sock.makefile()

        except ConnectionRefusedError:
            app_info = await self.dictator.application_info()
            owner = await self.dictator.fetch_user(app_info.team.owner_id)
            await owner.send('Is the game server offline? it did not respond to a stats request.')
            print('Server failed stats request, pinged my owner.')
            return 'Unknown'

        else:
            if 'SN' in fd.readline(128):
                count = fd.readline(128).split('/')
                return f'{count[0]}'

        finally:
            sock.close()
        
    async def get_open_collective_data(self):
        return
        
    async def average_total_income(self) -> int:
        return
    
    async def average_total_outgoing(self) -> int:
        return
        
    async def current_balance(self) -> int:
        return
            
    async def forecast_negative_cashflow_date(self, start_balance: int, incoming: int, outgoing: int) -> int:
        months = 0
        while start_balance > 0 and months <= 60:
            start_balance += incoming
            start_balance -= outgoing
            months += 1

        return (date.today() + relativedelta(months=+months)).strftime("%B")

    @commands.command()
    async def oc(self, ctx):
        print(await self.forecast_negative_cashflow_date(300, 50, 100))


async def setup(dictator):
    await dictator.add_cog(Stats(dictator))
