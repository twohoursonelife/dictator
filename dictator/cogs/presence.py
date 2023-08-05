import discord
from discord.ext import commands, tasks
from itertools import cycle


class Presence(commands.Cog):
    def __init__(self, dictator: commands.Bot) -> None:
        self.dictator = dictator

        self.status = cycle(
            # 1: Playing, 2: Listening to, 3: Watching, 5: Competing in
            [
                (3, "Kripts"),
                (2, "Twisted"),
                (1, "with Uno"),
                (3, "Sammoh shine"),
                (3, "over Newport"),
                (5, "Dictatorship"),
                (5, "cheese eating"),
                (5, "trolling Moon"),
                (2, "CartoonJessie"),
                (1, "for Five Years"),
                (2, "Hidei ho ho ho"),
                (5, "baking the pies"),
                (5, "munching berries"),
                (5, "bullying Tahtekcub"),
            ]
        )

    @commands.Cog.listener()
    async def on_ready(self):
        self.change_status.start()

    @tasks.loop(seconds=6)
    async def change_status(self):
        status = next(self.status)
        activity = discord.Activity(name=status[1], type=status[0])
        await self.dictator.change_presence(activity=activity)


async def setup(dictator: commands.Bot) -> None:
    await dictator.add_cog(Presence(dictator))
