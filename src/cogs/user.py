import discord
import mysql.connector
import re
import random
from textwrap import wrap
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
            username = user.name

        # Filter username, can't have any nasty characters
        # Then replaces any non whitlisted (regex) characters with empty string
        username = (re.sub('[^a-zA-Z0-9]', '', username))

        # Check if user already has an account before creating one
        check_user = await self.search_user(user.id)

        if check_user is not None:
            # User already has an account
            username = check_user[0]
            key = check_user[1]
            print(f'We tried to create an account for {user} but they already had one, so we\'ll send them their login information.')
            await user.send(f'Hey {user.mention}, you already have an account! Here is your login information:\n**Username:** {username}\n**Key:** {key}')
            return

        # Can't be having usernames too long, database allows for up to 255 but, seriously?
        if len(username) > 45:
            username = username[0:45]

        username += '-' + user.discriminator

        # Check if username is already in use
        check_name = await self.search_username(username)

        if check_name is not None:
            # Username already in use
            print(f'We tried to create an account for {user} but their username is already in use, prompting them for one.')
            await user.send(f'Hey {user.mention}, your username is already in use. What should I use instead?')
            try:
                def check(m):
                    # Make sure we're only listening for a message from the relevant user via DM
                    return m.author == user and isinstance(m.channel, discord.DMChannel)
                
                msg = await self.dictator.wait_for('message', timeout=60.0, check=check)

            except:
                print(f'{user} took too long to tell me what they wanted to set their username as.')
                await user.send('You didn\'t tell me what I should use as your username.')
                return

            else:
                await self.create_user(user, msg.content)
                return

        # Create the users accounnt, calling on create_key for a key
        key = str(await self.create_key())
        user_id = int(user.id)
        username = str(username)
        try:
            db = mysql.connector.connect(**config.db_config())
            cursor = db.cursor()
            cursor.execute(f'INSERT INTO users (email, discord_id, l_key) VALUES (\'{username}\', \'{user_id}\', \'{key}\')')
            db.commit()

        except mysql.connector.Error as e:
            print(f'\n\nMySQL Error\n{e}\n\n')
            return
        
        else:
            print(f'Successfully created an account for {username}.')
            await user.send(f'I\'ve successfully created an account for you. The following information will help you to download, log in and play our game.\nThere is important information in this message, I recommend you read it!\n\n**1. Download**\nGo to this link to download the game, make sure to download the correct version for your operating system.\nhttps://twohoursonelife.com/download \nThis will download a compressed folder, the next step will tell you what you need to do with this folder.\n\n**2. Install**\nInstalling the game is as simple as extracting the compressed folder.\n\n**Windows:** Right click the downloaded archive folder and select "Extract All...", then follow the prompts to save the game contents wherever available on your machine.\n**Mac:** Double click the downloaded archive folder to extract it to the current directory.\n**Ubuntu:** Right click the downloaded archive folder and select "Extract Here" or "Extract to..." to choose a different folder to extract to.\n*Linux may require other dependencies, contact a team member if you have trouble.*')
            await user.send(f'\n\n**3. Launching**\nOnce you have the game extracted, you\'ll find all of the necessary files to run the game inside the extracted folder.\nTo launch the game you will need to run the application within the extracted folder. The game application should be titled something like "2HOL_v20XXX" sometimes with other symbols and a version number.\nThe first time launching the game will take a lot longer than it will in future.\n\n**4. Logging in**\nOnce the game is loaded, you\'ll be presented with a mostly black log in screen. Enter the following details to play:\n**Username:** {username}\n**Key:** {key}\nThe game will save these details so you do not need to reenter them each time, make sure to keep them to yourself!\n\n**5. First time playing**\nThe first time you log in, you will be spawned in the tutorial.\nIn the tutorial, you are playing in the same world as every other player, but very far from civilisation.\nYou need to follow through the instructions and information in the tutorial to learn basic skills and how to play. At the end there will be a test of your skills which will then let you escape and play with others in your next life.\n\n**Need some help?**\nHead over to the #help channel in our Discord server, **explain exactly where you\'re stuck** and a friendly human will try to help you as soon as they can.\n\n**Other**\n- Look through the channels in the top of our discord for some helpful information about our discord and the game.\n- Chat with others in the discord to find some people to play with.\n- Use the command `-key` in the discord channel #bot-topic and I\'ll send you your log in information again.')
            return

        finally:
            cursor.close()
            db.close()

    # Generate a string consisting of 20 random chars, split into 4 chunks of 5 and seperated by -
    async def create_key(self):
        readable_base_32_digit_array = ["2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F", "G", "H", "J", "K", "L", "M", "N", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
        key = ""
        while len(key) != 20:
            key += readable_base_32_digit_array[random.randint(0, len(readable_base_32_digit_array) - 1)]

        key_chunks = wrap(key, 5)
        key = '-'.join(key_chunks)
        return key

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
            cursor.close()
            db.close()

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
            cursor.close()
            db.close()


def setup(dictator):
    dictator.add_cog(User(dictator))
