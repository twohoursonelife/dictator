import discord

dictator = discord.Client()

@dictator.event
async def on_ready():
    print('The 2HOL Dictator has risen!')

@dictator.event
async def on_message(message):
    if message.author == dictator.user:
        return

    if message.channel.name != ('bot-topic') or ('bot-channel'):
        return

    if message.content.startswith('-ping'):
        await message.channel.send('Pong!')


dictator.run('Key here')