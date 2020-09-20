import discord
from discord.ext import commands
import re
from utility.db_manager import db_connection as db_conn
import datetime


class Informational(commands.Cog):

    def __init__(self, dictator):
        self.dictator = dictator

    @commands.command(brief='Read the \'fricken\' manual.', help='Sends basic infoamtion about playing for the first time.')
    async def rtfm(self, ctx):
        await ctx.message.delete()
        await ctx.send(f'Heres the manual to play for the first time\n<https://twohoursonelife.com/first-time-playing>\n\nCheck your messages from me to find your username and password.')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.content == '.key' or message.content == '.mykey':
            await message.delete()
            await message.channel.send(f'{message.author.mention} You need to use `-key`', delete_after=10)

    @commands.command(aliases=['whois'], brief='Lookup who a player was in the game.', help='Lookup who a player was in the game. The player must have died. Only the last five results will be displayed. You will also be told how long ago each player died.')
    @commands.has_any_role('Admin', 'Mod', 'Well Experienced Player', 'Veteran Player', 'What is life?')
    async def whowas(self, ctx, *, character):
        await ctx.message.delete()

        # How many results to lookup.
        # Due to embed length limitations, the maxium is 8.
        history = 5

        # Friendly chars only thx
        character = re.sub(('[^a-zA-Z]'), '', character)

        with db_conn() as db:
            db.execute(f'SELECT discord_id, death_time, email FROM server_lives INNER JOIN users ON server_lives.user_id = users.id WHERE name = \'{character}\' ORDER BY death_time DESC LIMIT {history}')
            users = db.fetchall()

        if not users:
            embed = discord.Embed(title=f'No results for the character \'{character}\'.', colour=0xffbb35)
            await ctx.author.send(embed=embed)
            return

        current_time = datetime.datetime.now(tz=datetime.timezone.utc)
        current_time = current_time.replace(microsecond=0)
        embed = discord.Embed(title=f'Latest {history} results for the character \'{character}\':', colour=0xffbb35)

        for u in users:
            try:
                found_user = await self.dictator.fetch_user(u[0])

            except:
                raise commands.CommandError

            else:
                # Format death time as timezone aware
                death_time = datetime.datetime(year=u[1].year, month=u[1].month, day=u[1].day, hour=u[1].hour, minute=u[1].minute, second=u[1].second, tzinfo=datetime.timezone.utc)
                diff = current_time - death_time
                diff_split = str(diff).split(':')
                # diff_split[0] appears as '3 days, 4' where 3 = amount of days and 4 = amount of hours. I aplogise if you have to debug this.
                diff_formatted = f'{diff_split[0]} hours, {diff_split[1]} minutes ago'
                embed.add_field(name='Discord user:', value=f'{found_user}', inline=True)
                embed.add_field(name='Died:', value=f'{diff_formatted}', inline=True)
                embed.add_field(name='\u200b', value='\u200b')

        if len(users) < history:
            embed.add_field(name='\u200b', value='End of results')

        await ctx.author.send(embed=embed)


def setup(dictator):
    dictator.add_cog(Informational(dictator))
