"""Bot"""
import discord
from discord.ext import commands
import os
from os import listdir
from os.path import isfile, join
from web import db

from bot.helpers import logger
from bot.command import DiscordCommand

import web

bot = commands.Bot(command_prefix='!', case_insensitive=True)

ROOT = os.path.dirname(__file__)

# client = discord.Client()

@bot.check
async def check_if_can_respond(ctx):
  logger.info("%s: %s", ctx.author, ctx.message.content)
  #ignore DM
  if isinstance(ctx.channel, discord.abc.PrivateChannel):
    raise discord.ext.commands.CommandError("PM commands are not allowed. Please use the Imperium discord server.")

  return True

# hack to be able process admincomp commands from webhooks in the cog command (that my default disables bots)
@bot.listen()
async def on_message(message):
  if message.author.bot:
    ctx = await bot.get_context(message)
    await bot.invoke(ctx)

@bot.event
async def on_ready():
    """loads custom emojis upon ready"""
    logger.info('Logged in as')
    logger.info(bot.user.name)
    logger.info(bot.user.id)
    logger.info('------')
    # rewrite default discord emojis with the server supported ones
    for emoji in bot.emojis:
        DiscordCommand.emojis[emoji.name] = str(emoji)

    act = discord.Game("Imperium Season 3")
    await bot.change_presence(status=discord.Status.online, activity=act)

with open(os.path.join(ROOT, 'config/TOKEN'), 'r') as token_file:
    TOKEN = token_file.read()

cogs_dir = ROOT + "/bot/cogs"

# Here we load our extensions(cogs) that are located in the cogs directory. Any file in here attempts to load.
if __name__ == '__main__':
    for extension in [f.replace('.py', '') for f in listdir(cogs_dir) if isfile(join(cogs_dir, f))]:
        try:
            logger.info(f'Loading cog {extension}')
            bot.load_extension("bot.cogs." + extension)
        except (discord.ClientException, ModuleNotFoundError):
            logg.error(f'Failed to load extension {extension}.')

bot.run(TOKEN, bot=True, reconnect=True)

