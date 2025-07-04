import random

import discord
from discord import app_commands
from discord.ext import commands

from dictator.constants import MOD_ROLE_ID, OC_CHANNEL_ID


class System(commands.Cog):
    def __init__(self, dictator: commands.Bot) -> None:
        self.dictator = dictator

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Suppress all webhooks in the OC channel
        if not message.channel.id == OC_CHANNEL_ID:
            return

        if not message.webhook_id:
            return

        await message.edit(suppress=True)

    @app_commands.command()
    @app_commands.guild_only()
    async def ping(self, interaction: discord.Interaction) -> None:
        """Check the latency between Discord and Dictator."""

        if random.randint(1, 100) == 1:
            return await interaction.response.send_message(
                "Stop that, it hurts ;(", ephemeral=True
            )

        await interaction.response.send_message(
            f"Pong! That took me {round(self.dictator.latency * 1000)}ms to get a response from Discord!",
            ephemeral=True,
        )

    @commands.command(brief="Sync Dictators app commands globally.")
    @commands.guild_only()
    @commands.has_role(MOD_ROLE_ID)
    async def sync(self, ctx: commands.Context) -> None:
        await ctx.send(f"Synced `{len(await ctx.bot.tree.sync())}` commands globally.")


async def setup(dictator: commands.Bot) -> None:
    await dictator.add_cog(System(dictator))
