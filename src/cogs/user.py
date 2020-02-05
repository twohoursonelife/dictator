import discord
import mysql.connector
from discord.ext import commands
import config_manager as config


class User(commands.Cog):

    def __init__(self, dictator):
        self.dictator = dictator

    async def createKey(parameter_list):
        pass

    # Retrieve and send a users key information to themselves
    @commands.command()
    async def key(self, ctx):
        try:
            db = mysql.connector.connect(host=config.read('DB_host'), database=config.read(
                'DB_db'), user=config.read('DB_user'), password=config.read('DB_pass'))
            cursor = db.cursor()
            author_id = ctx.author.id
            cursor.execute(
                f"SELECT email, l_key FROM `users` WHERE discord_id = {author_id}")
            row = cursor.fetchone()

            username = row[0]
            key = row[1]

            await ctx.author.send(f'Hey {ctx.author.mention}! Here is your login information:\n**Username:** {username}\n**Key:** {key}')
            await ctx.send(f'{ctx.author.mention} I\'ve sent you a message with your login information.')

            print(f'Supplied username and key to {ctx.author}')

        except mysql.connector.Error as err:
            if err.errno == mysql.connector.errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)

        else:
            db.close()


def setup(dictator):
    dictator.add_cog(User(dictator))
