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
            db = mysql.connector.connect(**config.db_config())
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

        except mysql.connector.Error as e:
            print(e)
            await ctx.send(f'Uh oh... {ctx.guild.owner.mention} broke something again. Stand by.')

        else:
            db.close()


def setup(dictator):
    dictator.add_cog(User(dictator))
