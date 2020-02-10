import discord
import mysql.connector
from discord.ext import commands
import config_manager as config


class Admin(commands.Cog):

    def __init__(self, dictator):
        self.dictator = dictator

    @commands.command()
    @commands.has_role('Leader')
    async def ban(self, ctx, user, *, reason='The ban hammer has spoken.'):
        await ctx.message.delete()
        log_channel = await commands.TextChannelConverter().convert(ctx, config.read('log_channel_id'))
        
        # Ensure we're banning a valid user
        try:
            user = await commands.UserConverter().convert(ctx, user)

        except commands.CommandError:
            print(f'{ctx.author} tried to ban {user} but they\'re not a valid user.')
            ctx.author.send('You can only ban valid users.')

        # Check if user is already banned
        try:
            db = mysql.connector.connect(**config.db_config())
            cursor = db.cursor()
            cursor.execute(f'SELECT banned FROM `users` WHERE discord_id = \'{user.id}\'')
            row = cursor.fetchone()
            if row[0] is 1:
                print(f'{ctx.author} tried to ban {user} but they\'re already banned.')
                await ctx.author.send(f'{user.mention} is already banned.')
                return

        except mysql.connector.Error as e:
            print(f'\n\nMySQL Error\n{e}\n\n')
            return

        finally:
            cursor.close()
            db.close()

        # Ban the user
        try:
            db = mysql.connector.connect(**config.db_config())
            cursor = db.cursor()
            cursor.execute(f'UPDATE users SET banned = 1 WHERE discord_id = \'{user.id}\'')
            db.commit()

        except mysql.connector.Error as e:
            print(f'\n\nMySQL Error\n{e}\n\n')
            return

        else:
            print(f'{ctx.author} banned {user} for: {reason}')
            await ctx.author.send(f'You have **banned** {user.mention} for: {reason}')
            await user.send(f'Your account to play 2HOL has been **banned** for: {reason}\nIf you believe this has been done in error, contact a leader.')

            # Embed log
            embed = discord.Embed(title='User has been banned from the game', colour=discord.Colour.red())
            embed.add_field(name='User:', value=f'{user.mention}', inline=True)
            embed.add_field(name='Reason:', value=f'{reason}', inline=True)
            embed.add_field(name='Moderator:', value=f'{ctx.author.mention}', inline=True)
            await log_channel.send(embed=embed)
            return

        finally:
            cursor.close()
            db.close()

    @commands.command()
    @commands.has_role('Leader')
    async def unban(self, ctx, user, *, reason='It\'s your lucky day!'):
        await ctx.message.delete()
        log_channel = await commands.TextChannelConverter().convert(ctx, config.read('log_channel_id'))
        
        # Ensure we're unbanning a valid user
        try:
            user = await commands.UserConverter().convert(ctx, user)

        except commands.CommandError:
            print(f'{ctx.author} tried to unban {user} but they\'re not a valid user.')
            ctx.author.send('You can only unban valid users.')

        # Check that user is banned
        try:
            db = mysql.connector.connect(**config.db_config())
            cursor = db.cursor()
            cursor.execute(f'SELECT banned FROM `users` WHERE discord_id = \'{user.id}\'')
            row = cursor.fetchone()
            if row[0] is 0:
                print(f'{ctx.author} tried to unban {user} but they\'re not already banned.')
                await ctx.author.send(f'{user.mention} is not already banned.')
                return

        except mysql.connector.Error as e:
            print(f'\n\nMySQL Error\n{e}\n\n')
            return
        
        finally:
            cursor.close()
            db.close()

        # Unban the user
        try:
            db = mysql.connector.connect(**config.db_config())
            cursor = db.cursor()
            cursor.execute(f'UPDATE users SET banned = 0 WHERE discord_id = \'{user.id}\'')
            db.commit()

        except mysql.connector.Error as e:
            print(f'\n\nMySQL Error\n{e}\n\n')
            return

        else:
            print(f'{ctx.author} unbanned {user} for: {reason}')
            await ctx.author.send(f'You have **unbanned** {user.mention} for: {reason}')
            await user.send(f'Your account to play 2HOL has been **unbanned** for: {reason}')

            # Embed log
            embed = discord.Embed(title='User has been unbanned from the game', colour=discord.Colour.green())
            embed.add_field(name='User:', value=f'{user.mention}', inline=True)
            embed.add_field(name='Reason:', value=f'{reason}', inline=True)
            embed.add_field(name='Moderator:', value=f'{ctx.author.mention}', inline=True)
            await log_channel.send(embed=embed)
            return

        finally:
            cursor.close()
            db.close()


def setup(dictator):
    dictator.add_cog(Admin(dictator))
