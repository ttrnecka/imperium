"""Bot"""
import discord
from discord.ext import commands
import os
from web import db

from bot.helpers import logger
from bot.command import DiscordCommand

import web

bot = commands.Bot(command_prefix='!')

ROOT = os.path.dirname(__file__)

client = discord.Client()

@client.event
async def on_message(message):
    """Message event handler"""
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    #ignore DM
    if isinstance(message.channel, discord.abc.PrivateChannel):
        await message.channel.send(
            "PM commands are not allowed. Please use the Imperium discord server."
        )
        return

    #ignore commands not starting with !
    if not message.content.startswith("!"):
        return

    logger.info("%s: %s", message.author, message.content)

    try:
        command = DiscordCommand(message, client)
        await command.process()
    finally:
        db.session.close()

@client.event
async def on_ready():
    """loads custom emojis upon ready"""
    logger.info('Logged in as')
    logger.info(client.user.name)
    logger.info(client.user.id)
    logger.info('------')
    # rewrite default discord emojis with the server supported ones
    for emoji in client.emojis:
        DiscordCommand.emojis[emoji.name] = str(emoji)

    act = discord.Game("Imperium Season 3")
    await client.change_presence(status=discord.Status.online, activity=act)


with open(os.path.join(ROOT, 'config/TOKEN'), 'r') as token_file:
    TOKEN = token_file.read()

client.run(TOKEN)
