import socket
from datetime import datetime, time, timezone

from discord.ext import commands, tasks

from dictator.db_manager import db_connection
from dictator.logger_config import logger


class PlayerCounts(commands.Cog):
    def __init__(self, dictator: commands.Bot) -> None:
        self.dictator = dictator

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        if not self.record_player_count.is_running():
            self.record_player_count.start()

    def cog_unload(self):
        self.record_player_count.cancel()

    @tasks.loop(
        time=[
            time(hour=h, minute=m, tzinfo=timezone.utc)
            for h in range(24)
            for m in (0, 15, 30, 45)
        ]
    )
    async def record_player_count(self) -> None:
        count = await self.dictator.loop.run_in_executor(None, self.get_player_count)

        now = datetime.now(timezone.utc)
        # Force set to the minute
        recorded_time = now.replace(second=0, microsecond=0)

        with db_connection() as db:
            db.execute(
                "INSERT INTO player_counts (timestamp, player_count) VALUES (%s, %s)",
                (recorded_time, count),
            )

    def get_player_count(self) -> int | None:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(3.0)
                sock.connect(("play.twohoursonelife.com", 8005))
                fd = sock.makefile()
                if "SN" in fd.readline(128):
                    count_str = fd.readline(128).split("/")
                    return int(count_str[0])
        except (socket.timeout, OSError, ValueError, IndexError) as e:
            logger.error(f"Failed to fetch player count: {e}")
            return None
        return None


async def setup(dictator: commands.Bot) -> None:
    await dictator.add_cog(PlayerCounts(dictator))
