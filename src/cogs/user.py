import discord
import mysql.connector
from discord.ext import commands
import config_manager as config


class User(commands.Cog):

    def __init__(self, dictator):
        self.dictator = dictator

    async def createUser(self, user, user_id):
        pass

    async def createKey(self):
        pass

    async def search_user(self, user_id):
        try:
            db = mysql.connector.connect(**config.db_config())
            cursor = db.cursor()
            cursor.execute(f'SELECT email, l_key FROM `users` WHERE discord_id = {user_id}')
            row = cursor.fetchone()
            return row

        except mysql.connector.Error as e:
            print(f'\n\nMySQL Connection Error at user.py, check_user_exists()\n{e}\n\n')
            return

        finally:
            db.close

    # Retrieve and send a users login information to themselves
    @commands.command(aliases=['mykey'])
    async def key(self, ctx):
        user = await self.search_user(ctx.author.id)

        if user is None:
            await ctx.send(f'{ctx.author.mention} You don\'t have an account, I\'m creating one for you now. I\'ll send you a message soon!')
            await self.create_user(ctx.author)
            print(f'{ctx.author} attempted to retrieve their key but didn\'t have an account, we\'ll create them one.')

        else:
            username = user[0]
            key = user[1]
            await ctx.send(f'{ctx.author.mention} I\'ll send you a message with your login information.')
            await ctx.author.send(f'Hey {ctx.author.mention}! Here is your login information:\n**Username:** {username}\n**Key:** {key}')
            print(f'Supplied username and key to {ctx.author}')


def setup(dictator):
    dictator.add_cog(User(dictator))
