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

    @commands.command(brief=f'Claim the \'{ROLE_1["name"]}\' role.', help=f'If you have {ROLE_1["hours"]} or more hours in game, you can claim this role.')
    async def ncl(self, ctx):
        await ctx.message.delete()

        if self.already_has_role(ctx, ROLE_1["name"]):
            await ctx.send(f'{ctx.author.mention}, you already have this role!', delete_after=10)
            return

        if self.playtime_less_than(ctx.author.id, ROLE_1["hours"] * 60):
            await ctx.send(f'{ctx.author.mention}, you do not have {ROLE_1["hours"]} or more hours in game. Nearly!', delete_after=10)
            return
            
        await self.assign_role(ctx, ROLE_1["name"], "User claimed role")
        await ctx.send(f'Woohoo, {ctx.author.mention}! You have claimed the \'{ROLE_1["name"]}\' role, for playing {ROLE_1["hours"]} or more hours in game! *You\'re starting to know your way around!*')

    @commands.command(brief=f'Claim the \'{ROLE_2["name"]}\' role.', help=f'If you have {ROLE_2["hours"]} or more hours in game, you can claim this special role.')
    async def exp(self, ctx):
        await ctx.message.delete()

        if self.already_has_role(ctx, ROLE_2["name"]):
            await ctx.send(f'{ctx.author.mention}, you already have this role!', delete_after=10)
            return

        if self.playtime_less_than(ctx.author.id, ROLE_2["hours"] * 60):
            await ctx.send(f'{ctx.author.mention}, you do not have {ROLE_2["hours"]} or more hours in game. Keep on playin!', delete_after=10)
            return

        await self.assign_role(ctx, ROLE_2["name"], "User claimed role")
        await ctx.send(f'Congratulations, {ctx.author.mention}! You have claimed the \'{ROLE_2["name"]}\' role, for playing {ROLE_2["hours"]} or more hours in game! *Go take a break!*')

    @commands.command(brief=f'Claim the \'{ROLE_3["name"]}\' role.', help=f'If you have {ROLE_3["hours"]} or more hours in game, you can claim this extra special role.')
    async def vet(self, ctx):
        await ctx.message.delete()

        if self.already_has_role(ctx, ROLE_3["name"]):
            await ctx.send(f'{ctx.author.mention}, you already have this role!', delete_after=10)
            return

        if self.playtime_less_than(ctx.author.id, ROLE_3["hours"] * 60):
            await ctx.send(f'{ctx.author.mention}, you do not have {ROLE_3["hours"]} or more hours in game. Surely just a few more to go...!', delete_after=10)
            return
            
        await self.assign_role(ctx, ROLE_3["name"], "User claimed role")
        await ctx.send(f'Woah, {ctx.author.mention}! You have claimed the \'{ROLE_3["name"]}\' role, for playing {ROLE_3["hours"]} or more hours in game! *You\'re apart of the furniture now*')
    
    @commands.command(brief=f'Claim the \'{ROLE_4["name"]}\' role.', help=f'If you have {ROLE_4["hours"]} or more hours in game, you can claim this super extra special role.')
    async def wil(self, ctx):
        await ctx.message.delete()

        if self.already_has_role(ctx, ROLE_4["name"]):
            await ctx.send(f'{ctx.author.mention}, you already have this role! Doh!', delete_after=10)
            return

        if self.playtime_less_than(ctx.author.id, ROLE_4["hours"] * 60):
            await ctx.send(f'{ctx.author.mention}, you do not have {ROLE_4["hours"]} or more hours in game. Just around the corner, *right?*', delete_after=10)
            return
            
        await self.assign_role(ctx, ROLE_4["name"], "User claimed role")
        await ctx.send(f'Woah, {ctx.author.mention}! You have claimed the \'{ROLE_4["name"]}\' role, for playing {ROLE_4["hours"]} or more hours in game! *I suppose you can go now*')

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
