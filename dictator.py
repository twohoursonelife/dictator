import discord

class dictator(discord.Client):
    async def on_ready(self):
        print('2HOL Dictator has risen!')

client = dictator()
client.run('Token here')