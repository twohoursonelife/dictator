import discord
from discord.ext import commands
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

    @commands.command(brief='See info about a user.', help='Sends you a message containing information about a user.', usage='<user>')
    @commands.guild_only()
    async def info(self, ctx, user: discord.User):
        await ctx.message.delete()

        with db_conn() as db:
            db.execute(f'SELECT life_count, time_played, last_activity, banned, email FROM users WHERE discord_id = \'{user.id}\'')
            user_info = db.fetchone()

        if not user_info:
            embed = discord.Embed(title=f'No results for the user \'{user.mention}\'.', colour=0xffbb35)
            await ctx.author.send(embed=embed)
            return

        # User hasn't lived a single life yet
        if user_info[0] == None:
            embed = discord.Embed(title=f'\'{user.name}#{user.discriminator}\' has not lived any lives yet.', colour=0xffbb35)
            await ctx.author.send(embed=embed)
            return

        # Time formatting
        current_time = datetime.datetime.now(tz=datetime.timezone.utc)
        current_time = current_time.replace(microsecond=0)
        last_active = datetime.datetime(year=user_info[2].year, month=user_info[2].month, day=user_info[2].day, hour=user_info[2].hour, minute=user_info[2].minute, second=user_info[2].second, tzinfo=datetime.timezone.utc)
        diff = current_time - last_active
        diff_split = str(diff).split(':')
        # diff_split[0] appears as '3 days, 4' where 3 = amount of days and 4 = amount of hours. I aplogise if you have to debug this.
        diff_formatted = f'{diff_split[0]} hours, {diff_split[1]} minutes ago'

        member = ctx.guild.get_member(user.id)

        # Form embed
        embed = discord.Embed(title=f'Results for the user \'{user.name}#{user.discriminator}\':', colour=0xffbb35)
        embed.add_field(name='Life count:', value=user_info[0])
        embed.add_field(name='Time played:', value=f'{round(user_info[1] / 60, 1)} hours')
        embed.add_field(name='Last death:', value=diff_formatted)
        embed.add_field(name='Banned:', value='Yes' if user_info[3] else 'No')
        embed.add_field(name='Joined guild:', value=member.joined_at.date() if member else 'Unknown')
        embed.add_field(name='Username:', value=user_info[4])
        embed.set_footer(text='Data range: August 2019 - Current')
        await ctx.author.send(embed=embed)


def setup(dictator):
    dictator.add_cog(Informational(dictator))
