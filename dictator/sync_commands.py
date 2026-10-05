import asyncio

from dictator.dictator import dictator
from dictator.logger_config import logger
from dictator.settings import config


async def sync_commands() -> None:
    """Sync application commands with Discord."""
    async with dictator:
        await dictator.login(config.BOT_TOKEN)
        synced_commands = await dictator.tree.sync()

    logger.info(f"Synced {len(synced_commands)} application commands.")


if __name__ == "__main__":
    asyncio.run(sync_commands())
