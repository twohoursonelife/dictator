import discord
from discord.ext import commands
from utility.db_manager import db_connection as db_conn


class Ranks(commands.Cog):

    def __init__(self, dictator):
        self.dictator = dictator

    @commands.command(brief='Claim the \'Well Experienced Player\' rank.', help='If you have 50 or more hours in game, you can claim this special rank.')
    async def exp(self, ctx):
        await ctx.message.delete()

        # Does the user already have the role?
        user_has_role = discord.utils.get(ctx.author.roles, name='Well Experienced Player')
        if user_has_role != None:
            await ctx.send(f'{ctx.author.mention}, you already have this role!', delete_after=10)
            return

        with db_conn() as db:
            db.execute(f'SELECT time_played FROM users WHERE discord_id = {ctx.author.id}')
            time = db.fetchone()

        # This user does not have 50 hours in game (Data is in minutes)
        if int(time[0]) < 3000:
            await ctx.send(f'{ctx.author.mention}, you do not have 50 or more hours in game. Keep on playin!', delete_after=10)
            return

        # All seems good, award the player their role!
        role = discord.utils.get(ctx.guild.roles, name='Well Experienced Player')
        await ctx.author.add_roles(role, reason='User claimed role.')
        await ctx.send(f'Congratulations, {ctx.author.mention}! You have claimed the \'Well Experienced Player\' role, for playing 50 or more hours in game! *Go take a break!*')


def setup(dictator):
    dictator.add_cog(Ranks(dictator))
