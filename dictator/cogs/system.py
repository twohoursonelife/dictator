import discord
from discord import app_commands

from discord.ext import commands

import random

class System(commands.Cog):

    def __init__(self, dictator: commands.Bot) -> None:
        self.dictator = dictator

    @app_commands.command()
    async def ping(self, interaction: discord.Interaction) -> None:
        """Check the latency between Discord and Dictator."""
        
        if random.randint(1, 100) == 1:
            return await interaction.response.send_message(f"Stop that, it hurts ;(", ephemeral=True)
        
        await interaction.response.send_message(f"Pong! That took me {round(self.dictator.latency * 1000)}ms to get a response from Discord!", ephemeral=True)
        
    @app_commands.command()    
    async def version(self, interaction: discord.Interaction) -> None:
        """Check the current version of Dictator."""
        
        try:
            with open('version.txt', 'r') as file:
                await interaction.response.send_message(file.read(), ephemeral=True)
        
        except FileNotFoundError:
            await interaction.response.send_message("Version unknown.", ephemeral=True)
            
            
    @commands.guild_only()
    @commands.is_owner()
    @commands.command(brief='Sync Dictators app commands globally.')
    async def sync(self, ctx: commands.Context) -> None:
        synced = await ctx.bot.tree.sync()
        await ctx.send(f'Synced `{len(synced)}` commands globally.')


async def setup(dictator: commands.Bot) -> None:
    await dictator.add_cog(System(dictator))
