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
            db.execute(f'SELECT time_played FROM ticketServer_tickets WHERE discord_id = {ctx.author.id}')
            time = db.fetchone()

        # This user does not have 50 hours in game (Data is in minutes)
        if int(time[0]) < 3000:
            await ctx.send(f'{ctx.author.mention}, you do not have 50 or more hours in game. Keep on playin!', delete_after=10)
            return

        # All seems good, award the player their role!
        role = discord.utils.get(ctx.guild.roles, name='Well Experienced Player')
        await ctx.author.add_roles(role, reason='User claimed role.')
        await ctx.send(f'Congratulations, {ctx.author.mention}! You have claimed the \'Well Experienced Player\' role, for playing 50 or more hours in game! *Go take a break!*')

    @commands.command(brief='Claim the \'Veteran Player\' rank.', help='If you have 375 or more hours in game, you can claim this extra special rank.')
    async def vet(self, ctx):
        await ctx.message.delete()

        # Does the user already have the role?
        user_has_role = discord.utils.get(ctx.author.roles, name='Veteran Player')
        if user_has_role != None:
            await ctx.send(f'{ctx.author.mention}, you already have this role!', delete_after=10)
            return

        with db_conn() as db:
            db.execute(f'SELECT time_played FROM ticketServer_tickets WHERE discord_id = {ctx.author.id}')
            time = db.fetchone()

        # This user does not have 375 hours in game (Data is in minutes)
        if int(time[0]) < 22500:
            await ctx.send(f'{ctx.author.mention}, you do not have 375 or more hours in game. Surely just a few more to go...!', delete_after=10)
            return

        # All seems good, award the player their role!
        role = discord.utils.get(ctx.guild.roles, name='Veteran Player')
        await ctx.author.add_roles(role, reason='User claimed role.')
        await ctx.send(f'Woah, {ctx.author.mention}! You have claimed the \'Veteran Player\' role, for playing 375 or more hours in game! *You\'re apart of the furniture now*')


def setup(dictator):
    dictator.add_cog(Ranks(dictator))
