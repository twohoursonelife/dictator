import discord
from discord.ext import commands
from utility.db_manager import db_connection as db_conn

# Roles ["Role name, must match Discord", Required hours]
ROLE_1 = {"name": "Not Completely Lost", "hours": 10}
ROLE_2 = {"name": "Well Experienced", "hours": 50}
ROLE_3 = {"name": "Veteran", "hours": 375}
ROLE_4 = {"name": "What is life?", "hours": 1000}

class Roles(commands.Cog):

    def __init__(self, dictator):
        self.dictator = dictator

    @commands.command(brief='Claim the \'Not Completely Lost\' role.', help='If you have 10 or more hours in game, you can claim this special role.')
    async def ncl(self, ctx):
        await ctx.message.delete()

        if self.already_has_role(ctx, "Not Completely Lost"):
            await ctx.send(f'{ctx.author.mention}, you already have this role!', delete_after=10)
            return

        # 10 hours = 600 minutes
        if self.playtime_less_than(ctx.author.id, 600):
            await ctx.send(f'{ctx.author.mention}, you do not have 10 or more hours in game. Nearly!', delete_after=10)
            return
            
        await self.assign_role(ctx, "Not Completely Lost", "User claimed role")
        await ctx.send(f'Woohoo, {ctx.author.mention}! You have claimed the \'Not Completely Lost\' role, for playing 10 or more hours in game! *You\'re starting to know your way around!*')

    @commands.command(brief='Claim the \'Well Experienced\' role.', help='If you have 50 or more hours in game, you can claim this special role.')
    async def exp(self, ctx):
        await ctx.message.delete()

        if self.already_has_role(ctx, "Well Experienced"):
            await ctx.send(f'{ctx.author.mention}, you already have this role!', delete_after=10)
            return

        # 50 hours = 3000 minutes
        if self.playtime_less_than(ctx.author.id, 3000):
            await ctx.send(f'{ctx.author.mention}, you do not have 50 or more hours in game. Keep on playin!', delete_after=10)
            return

        await self.assign_role(ctx, "Well Experienced", "User claimed role")
        await ctx.send(f'Congratulations, {ctx.author.mention}! You have claimed the \'Well Experienced\' role, for playing 50 or more hours in game! *Go take a break!*')

    @commands.command(brief='Claim the \'Veteran\' role.', help='If you have 375 or more hours in game, you can claim this extra special role.')
    async def vet(self, ctx):
        await ctx.message.delete()

        if self.already_has_role(ctx, "Veteran"):
            await ctx.send(f'{ctx.author.mention}, you already have this role!', delete_after=10)
            return

        # 375 hours = 22500 minutes
        if self.playtime_less_than(ctx.author.id, 22500):
            await ctx.send(f'{ctx.author.mention}, you do not have 375 or more hours in game. Surely just a few more to go...!', delete_after=10)
            return
            
        await self.assign_role(ctx, "Veteran", "User claimed role")
        await ctx.send(f'Woah, {ctx.author.mention}! You have claimed the \'Veteran\' role, for playing 375 or more hours in game! *You\'re apart of the furniture now*')
    
    def already_has_role(self, ctx, role):
        role_object = discord.utils.get(ctx.author.roles, name=role)
        if role_object != None:
            return True
        return False

    async def assign_role(self, ctx, role, reason):
        role_object = discord.utils.get(ctx.guild.roles, name=role)
        await ctx.author.add_roles(role_object, reason=reason)

    def playtime_less_than(self, discord_id, less_than_minutes):
        with db_conn() as db:
            db.execute(f'SELECT time_played FROM ticketServer_tickets WHERE discord_id = {discord_id}')
            time_played = db.fetchone()
        
        return True if int(time_played[0]) < less_than_minutes else False


def setup(dictator):
    dictator.add_cog(Roles(dictator))
