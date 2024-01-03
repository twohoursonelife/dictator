import discord
from discord import app_commands
from discord.ext import commands

from constants import MOD_ROLE_ID, OC_CHANNEL_ID
from get_version import get_dictator_version

import random
import logging


class System(commands.Cog):
    def __init__(self, dictator: commands.Bot) -> None:
        self.dictator = dictator
        logging.basicConfig(level=logging.INFO)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not message.channel.id == OC_CHANNEL_ID:
            return
        
        logging.info(f"Message sent in OC channel ({message.id})")

        if not message.webhook_id:
            return
        
        logging.info(f"Message sent by webhook ({message.id})")

        if message.embeds:
            await message.edit(suppress=True)
            logging.info(f"Message edited ({message.id})")
            return
        
        logging.info(f"Message not edited ({message.id})")
            

    @app_commands.command()
    async def ping(self, interaction: discord.Interaction) -> None:
        """Check the latency between Discord and Dictator."""

        if random.randint(1, 100) == 1:
            return await interaction.response.send_message(
                f"Stop that, it hurts ;(", ephemeral=True
            )

        await interaction.response.send_message(
            f"Pong! That took me {round(self.dictator.latency * 1000)}ms to get a response from Discord!",
            ephemeral=True,
        )

    @app_commands.command()
    async def version(self, interaction: discord.Interaction) -> None:
        """Check the current version of Dictator."""
        await interaction.response.send_message(get_dictator_version(), ephemeral=True)

    @commands.guild_only()
    @app_commands.checks.has_role(MOD_ROLE_ID)
    @commands.command(brief="Sync Dictators app commands globally.")
    async def sync(self, ctx: commands.Context) -> None:
        synced = await ctx.bot.tree.sync()
        await ctx.send(f"Synced `{len(synced)}` commands globally.")


async def setup(dictator: commands.Bot) -> None:
    await dictator.add_cog(System(dictator))
