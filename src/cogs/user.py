import discord
import mysql.connector
import re
from discord.ext import commands
import config_manager as config


class User(commands.Cog):

    def __init__(self, dictator):
        self.dictator = dictator

    # Retrieve and send a users login information to themselves
    @commands.command(aliases=['mykey'])
    @commands.guild_only()
    async def key(self, ctx):
        user = await self.search_user(ctx.author.id)

        if user is None:
            await ctx.send(f'{ctx.author.mention} You don\'t have an account, I\'m creating one for you now. I\'ll send you a message soon!')
            print(f'{ctx.author} attempted to retrieve their key but didn\'t have an account, we\'ll create them one.')
            await self.create_user(ctx.author)

        else:
            username = user[0]
            key = user[1]
            await ctx.send(f'{ctx.author.mention} I\'ll send you a message with your login information.')
            await ctx.author.send(f'Hey {ctx.author.mention}! Here is your login information:\n**Username:** {username}\n**Key:** {key}')
            print(f'Supplied username and key to {ctx.author}')

    async def create_user(self, user, username=None):
        if username is None:
            username = user

        # Filter username, can't have any nasty characters
        # Replaces # at beginning of discord discriminator with - 
        username = str(username).replace('#', '-')
        # Then replaces any non whitlisted (regex) characters with empty string
        username = re.sub('[^a-zA-Z0-9-]', '', username)

        # Check if user already has an account before creating one
        check_user = await self.search_user(user.id)

        if check_user is not None:
            # User already has an account
            username = check_user[0]
            key = check_user[1]
            print(f'We tried to create an account for {user} but they already had one, so we\'ll send them their login information.')
            await user.send(f'Hey {user.mention}, you already have an account! Here is your login information:\n**Username:** {username}\n**Key:** {key}')
            return

        # Check if username is already in use
        check_name = await self.search_username(username)

        if check_name is not None:
            # Username already in use
            print(f'We tried to create an account for {user} but their username is already in use, prompting them for one.')
            await user.send(f'Hey {user.mention}, your username is already in use. What should I use instead?')
            try:
                message = await self.dictator.wait_for('message', timeout=60.0)
                username = message.content
                username += f"-{user.discriminator}"
                await self.create_user(user, username)
                return
            except asyncio.TimeoutError:
                print(f'{user} took too long to tell me what they wanted to set their username as.')
                user.send('You didn\'t tell me what I should use as your username instead. You\'ll need to type -key to start again.')

        # Create the users accounnt, calling on create_key for a key

    async def create_key(self):
        pass

    # Search whether a user exists, return username and key if they do
    async def search_user(self, user_id):
        try:
            db = mysql.connector.connect(**config.db_config())
            cursor = db.cursor()
            cursor.execute(f'SELECT email, l_key FROM `users` WHERE discord_id = \'{user_id}\'')
            row = cursor.fetchone()
            return row

        except mysql.connector.Error as e:
            print(f'\n\nMySQL Error\n{e}\n\n')
            return

        finally:
            db.close

    # Search whether a username already exists
    async def search_username(self, user):
        try:
            db = mysql.connector.connect(**config.db_config())
            cursor = db.cursor()
            cursor.execute(f'SELECT email FROM `users` WHERE email = \'{user}\'')
            row = cursor.fetchone()
            return row

        except mysql.connector.Error as e:
            print(f'\n\nMySQL Error\n{e}\n\n')
            return

        finally:
            db.close


def setup(dictator):
    dictator.add_cog(User(dictator))
