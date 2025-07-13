import os

import discord
import sentry_sdk
from discord.ext import commands

from dictator.constants import (
    BOT_PREFIX,
    BOT_TOKEN,
    DICTATOR_VERSION,
    SENTRY_DSN,
    SENTRY_ENVIRONMENT,
)
from dictator.logger_config import logger

sentry_sdk.init(
    dsn=SENTRY_DSN,
    environment=SENTRY_ENVIRONMENT,
    release=DICTATOR_VERSION,
    traces_sample_rate=1.0,
)


class Dictator(commands.Bot):
    async def setup_hook(self) -> None:
        for filename in os.listdir("dictator/cogs"):
            if filename.endswith(".py"):
                await dictator.load_extension(f"dictator.cogs.{filename[:-3]}")


intents = discord.Intents.all()
dictator = Dictator(command_prefix=BOT_PREFIX, case_insensitive=True, intents=intents)


@dictator.event
async def on_ready() -> None:
    logger.info("The 2HOL Dictator has risen!")


dictator.run(BOT_TOKEN)
