import discord
import mysql.connector
import re
import random
from textwrap import wrap
from discord.ext import commands
import utility.config_manager as config


class User(commands.Cog):

    def __init__(self, dictator):
        self.dictator = dictator

    # Retrieve and send a users login information to themselves
    @commands.command(aliases=['mykey'], brief='Retireve your login information for the game.', help='Retireve your login information for the game. If you don\'t have an account, one will be created for you.')
    @commands.guild_only()
    @commands.max_concurrency(1, per=commands.BucketType.user, wait=False)
    async def key(self, ctx):
        user = await self.search_user(ctx.author.id)

        if user is None:
            await ctx.send(f'{ctx.author.mention} You don\'t have an account, I\'m creating one for you now. I\'ll send you a message soon!', delete_after=10)
            print(
                f'{ctx.author} attempted to retrieve their key but didn\'t have an account, we\'ll create them one.')
            await self.create_user(ctx.author)

        else:
            username = user[0]
            key = user[1]
            await ctx.send(f'{ctx.author.mention} I\'ll send you a message with your login information.', delete_after=10)
            await ctx.author.send(f'Hey {ctx.author.mention}! Here is your login information:\n**Username:** {username}\n**Key:** {key}')
            print(f'Supplied username and key to {ctx.author}')

        await ctx.message.delete()

    async def create_user(self, user, username=None):
        if username is None:
            username = user.name

        # Filter username, can't have any nasty characters
        # Then replaces any non whitlisted (regex) characters with empty string
        username = (re.sub('[^a-zA-Z0-9]', '', username))

        if len(username) < 3:
            # Username was only made up of special chracters, prompt for one
            chosen_username = await self.prompt_user(user, f'Hey {user.mention}, your username doesn\'t contain enough valid characters. What should I use instead?')

            if chosen_username is None:
                await user.send('You didn\'t tell me what to use instead.')
                return

            else:
                await self.create_user(user, chosen_username)
                return

        # Check if user already has an account before creating one
        check_user = await self.search_user(user.id)

        if check_user is not None:
            # User already has an account
            username = check_user[0]
            key = check_user[1]
            print(
                f'We tried to create an account for {user} but they already had one, so we\'ll send them their login information.')
            await user.send(f'Hey {user.mention}, you already have an account! Here is your login information:\n**Username:** {username}\n**Key:** {key}')
            return

        # Can't be having usernames too long, database allows for up to 255 but seriously?
        if len(username) > 45:
            username = username[0:45]

        username += '-' + user.discriminator

        # Check if username is already in use
        check_name = await self.search_username(username)

        if check_name is not None:
            # Username is already in use, prompt for one
            chosen_username = await self.prompt_user(user, f'Hey {user.mention}, your username is already in use. What should I use instead?')

            if chosen_username is None:
                await user.send('You didn\'t tell me what to use instead.')
                return

            else:
                await self.create_user(user, chosen_username)
                return

        # Create the users accounnt, calling on create_key for a key
        key = str(await self.create_key())
        user_id = int(user.id)
        username = str(username)
        try:
            db = mysql.connector.connect(**config.db_config())

            if db.is_connected:
                cursor = db.cursor()
                cursor.execute(
                    f'INSERT INTO users (email, discord_id, l_key) VALUES (\'{username}\', \'{user_id}\', \'{key}\')')
                db.commit()

        except mysql.connector.Error as e:
            raise e

        else:
            cursor.close()
            db.close()
            print(
                f'Successfully created an account for {user.name}#{user.discriminator} using the username {username}.')
            await user.send(f'Welcome to 2HOL {user.mention}!\nYou can read how to start playing our game at <https://twohoursonelife.com/first-time-playing>\nWhen you\'re ready, you can use the details below to log in to the game:\n**Username:** {username}\n**Key:** {key}')

    # Generate a string consisting of 20 random chars, split into 4 chunks of 5 and seperated by -
    async def create_key(self):
        readable_base_32_digit_array = ["2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E",
                                        "F", "G", "H", "J", "K", "L", "M", "N", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
        key = ""
        while len(key) != 20:
            key += readable_base_32_digit_array[random.randint(
                0, len(readable_base_32_digit_array) - 1)]

        key_chunks = wrap(key, 5)
        key = '-'.join(key_chunks)
        return key

    # Search whether a user exists, return username and key if they do
    async def search_user(self, user_id):
        try:
            db = mysql.connector.connect(**config.db_config())

            if db.is_connected():
                cursor = db.cursor(buffered=True)
                cursor.execute(
                    f'SELECT email, l_key FROM `users` WHERE discord_id = \'{user_id}\'')
                row = cursor.fetchone()
                return row

        except mysql.connector.Error as e:
            raise e

        else:
            cursor.close()
            db.close()

    # Search whether a username already exists
    async def search_username(self, user):
        try:
            db = mysql.connector.connect(**config.db_config())

            if db.is_connected():
                cursor = db.cursor()
                cursor.execute(
                    f'SELECT email FROM `users` WHERE email = \'{user}\'')
                row = cursor.fetchone()
                return row

        except mysql.connector.Error as e:
            raise e

        else:
            cursor.close()
            db.close()

    # Prompt user to respond to a question via private message
    async def prompt_user(self, user, msg):
        await user.send(f'{msg}')
        try:
            def check(m):
                # Make sure we're only listening for a message from the relevant user via DM
                return m.author == user and isinstance(m.channel, discord.DMChannel)

            reply = await self.dictator.wait_for('message', timeout=60.0, check=check)

        except:
            return

        else:
            return reply.content


def setup(dictator):
    dictator.add_cog(User(dictator))
