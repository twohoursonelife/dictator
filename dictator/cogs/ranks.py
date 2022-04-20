import discord
from discord.ext import commands
from utility.db_manager import db_connection as db_conn


class Ranks(commands.Cog):

    def __init__(self, dictator):
        self.dictator = dictator

    @commands.command(brief='Claim the \'Well Experienced\' rank.', help='If you have 50 or more hours in game, you can claim this special rank.')
    async def exp(self, ctx):
        await ctx.message.delete()

        if self.already_has_role(ctx, "Well Experienced"):
            await ctx.send(f'{ctx.author.mention}, you already have this role!', delete_after=10)
            return

        with db_conn() as db:
            db.execute(f'SELECT time_played FROM ticketServer_tickets WHERE discord_id = {ctx.author.id}')
            time = db.fetchone()

        # This user does not have 50 hours in game (Data is in minutes)
        if int(time[0]) < 3000:
            await ctx.send(f'{ctx.author.mention}, you do not have 50 or more hours in game. Keep on playin!', delete_after=10)
            return

        self.assign_role(ctx, "Well Experienced", "User claimed role")
        await ctx.send(f'Congratulations, {ctx.author.mention}! You have claimed the \'Well Experienced\' role, for playing 50 or more hours in game! *Go take a break!*')

    @commands.command(brief='Claim the \'Veteran\' rank.', help='If you have 375 or more hours in game, you can claim this extra special rank.')
    async def vet(self, ctx):
        await ctx.message.delete()

        if self.already_has_role(ctx, "Veteran"):
            await ctx.send(f'{ctx.author.mention}, you already have this role!', delete_after=10)
            return

        with db_conn() as db:
            db.execute(f'SELECT time_played FROM ticketServer_tickets WHERE discord_id = {ctx.author.id}')
            time = db.fetchone()

        # This user does not have 375 hours in game (Data is in minutes)
        if int(time[0]) < 22500:
            await ctx.send(f'{ctx.author.mention}, you do not have 375 or more hours in game. Surely just a few more to go...!', delete_after=10)
            return

        self.assign_role(ctx, "Veteran", "User claimed role")
        await ctx.send(f'Woah, {ctx.author.mention}! You have claimed the \'Veteran\' role, for playing 375 or more hours in game! *You\'re apart of the furniture now*')
    
    def already_has_role(self, ctx, role):
        role_object = discord.utils.get(ctx.author.roles, name=role)
        if role_object != None:
            return True
        return False

    async def assign_role(self, ctx, role, reason):
        role_object = discord.utils.get(ctx.guild.roles, name=role)
        await ctx.author.add_roles(role_object, reason=reason)


def setup(dictator):
    dictator.add_cog(Ranks(dictator))
