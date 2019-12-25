import discord
import logging

# Ensure to create a token.txt file in the same directory as this file which contains only the token of the bot.

dictator = discord.Client()

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.WARNING)

@dictator.event
async def on_ready():
    print('The 2HOL Dictator has risen!')

@dictator.event
async def on_message(message):
    if message.author == dictator.user:
        return

    if message.channel.name != ('bot-channel'):
        return

    if message.content.startswith('-ping'):
        logging.debug('Ive been pinged!')
        await message.channel.send('Pong!')

token = open('token.txt', 'r')
dictator.run(token.readline())
token.close