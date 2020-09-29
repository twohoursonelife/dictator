import discord
from discord.ext import commands
import utility.config_manager as config
from utility.db_manager import db_connection as db_conn
import datetime
import re


class Admin(commands.Cog):

    def __init__(self, dictator):
        self.dictator = dictator

    @commands.command(brief='Ban a user from the game.', help='Ban a user from the game. Any words after declaring the user will be the ban reason, if a reason is not specified it will default to "The ban hammer has spoken." The user, moderator and log channel will be notified. The user argument can be a Discord user tag, a Discord username with discriminator or a Discord user ID.', usage='<user> [reason]')
    @commands.has_role('Admin')
    async def ban(self, ctx, user: discord.User, *, reason='The ban hammer has spoken.'):
        await ctx.message.delete()
        log_channel = await commands.TextChannelConverter().convert(ctx, config.read('log_channel_id'))

        # Check if user is already banned
        with db_conn() as db:
            db.execute(f'SELECT banned FROM `users` WHERE discord_id = \'{user.id}\'')
            row = db.fetchone()

        if row[0] == 1:
            print(f'{ctx.author} tried to ban {user} but they\'re already banned.')
            await ctx.author.send(f'{user.mention} is already banned.')
            return

        # Ban the user
        with db_conn() as db:
            db.execute(f'UPDATE users SET banned = 1 WHERE discord_id = \'{user.id}\'')

        print(f'{ctx.author} banned {user} for: {reason}')

        # Notify the user
        try:
            embed = discord.Embed(title='You were banned from 2HOL', colour=discord.Colour.red())
            embed.add_field(name='Reason:', value=f'{reason}', inline=True)
            await user.send(embed=embed)

        except:
            notify_user = False

        else:
            notify_user = True

        # Embed log
        embed = discord.Embed(title='User banned from the game', colour=discord.Colour.red())
        embed.add_field(name='User:', value=f'{user.mention}', inline=True)
        embed.add_field(name='Reason:', value=f'{reason}', inline=True)
        embed.add_field(name='Moderator:', value=f'{ctx.author.mention}', inline=True)
        embed.add_field(name='User notification:', value='Successful' if notify_user else 'Failed', inline=True)
        await log_channel.send(embed=embed)

    @commands.command(brief='Unban a user from the game.', help='Unban a user from the game. Any words after declaring the user will be the unban reason, if a reason is not specified it will default to "It\'s your lucky day!" The user, moderator and log channel will be notified. The user argument can be a Discord user tag, a Discord username with discriminator or a Discord user ID.', usage='<user> [reason]')
    @commands.has_role('Admin')
    async def unban(self, ctx, user: discord.User, *, reason='It\'s your lucky day!'):
        await ctx.message.delete()
        log_channel = await commands.TextChannelConverter().convert(ctx, config.read('log_channel_id'))

        # Check that user is banned
        with db_conn() as db:
            db.execute(f'SELECT banned FROM `users` WHERE discord_id = \'{user.id}\'')
            row = db.fetchone()

        if row[0] == 0:
            print(f'{ctx.author} tried to unban {user} but they\'re not already banned.')
            await ctx.author.send(f'{user.mention} is not already banned.')
            return

        # Unban the user
        with db_conn() as db:
            db.execute(f'UPDATE users SET banned = 0 WHERE discord_id = \'{user.id}\'')

        print(f'{ctx.author} unbanned {user} for: {reason}')

        # Notify the user
        try:
            embed = discord.Embed(title='You were unbanned from 2HOL', colour=discord.Colour.green())
            embed.add_field(name='Reason:', value=f'{reason}', inline=True)
            await user.send(embed=embed)

        except:
            notify_user = False

        else:
            notify_user = True

        # Embed log
        embed = discord.Embed(title='User unbanned from the game', colour=discord.Colour.green())
        embed.add_field(name='User:', value=f'{user.mention}', inline=True)
        embed.add_field(name='Reason:', value=f'{reason}', inline=True)
        embed.add_field(name='Moderator:', value=f'{ctx.author.mention}', inline=True)
        embed.add_field(name='User notification:', value='Successful' if notify_user else 'Failed', inline=True)
        await log_channel.send(embed=embed)

    @commands.command(aliases=['regen'], brief='Regenerate a users key.', help='Regenerate a users key. This should be used when a users account is leaked.')
    @commands.has_any_role('Admin', 'Mod')
    async def regenerate(self, ctx, user: discord.User):
        await ctx.message.delete()

        log_channel = await commands.TextChannelConverter().convert(ctx, config.read('log_channel_id'))

        key = await self.dictator.get_cog('User').create_key()

        with db_conn() as db:
            db.execute(f'UPDATE users SET l_key = \'{key}\' WHERE discord_id = \'{user.id}\'')

        # Notify the user
        try:
            embed = discord.Embed(title='Your key to access 2HOL has been regenerated.', colour=discord.Colour.green())
            await user.send(embed=embed)

        except:
            notify_user = False

        else:
            notify_user = True

        # Embed log
        embed = discord.Embed(title='User key regenerated', colour=discord.Colour.green())
        embed.add_field(name='User:', value=f'{user.mention}', inline=True)
        embed.add_field(name='Moderator:', value=f'{ctx.author.mention}', inline=True)
        embed.add_field(name='User notification:', value='Successful' if notify_user else 'Failed', inline=True)
        await log_channel.send(embed=embed)

    @commands.command(aliases=['whois'], brief='Lookup who a player was in the game.', help='Lookup who a player was in the game. The player must have died. Only the last five results will be displayed. You will also be told how long ago each player died.')
    @commands.has_any_role('Team', 'Supporters', 'Well Experienced Player', 'Veteran Player', 'What is life?')
    async def whowas(self, ctx, *, character):
        await ctx.message.delete()

        # How many results to lookup.
        # Due to embed length limitations, the maxium is 8.
        history = 5

        # Friendly chars only thx
        character = re.sub(('[^a-zA-Z ]'), '', character)

        with db_conn() as db:
            db.execute('SELECT discord_id, death_time, email FROM server_lives INNER JOIN users ON server_lives.user_id = users.id WHERE name = %s ORDER BY death_time DESC LIMIT %s', (character, history))
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
    dictator.add_cog(Admin(dictator))
