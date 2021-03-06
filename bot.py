"""Bot"""
import os
import discord
from discord.ext import commands
from bot.helpers import logger, ImperiumHelpCommand, wastebasket_emoji
from misc.helpers import PackHelper
from misc.helpers2 import current_season
from web import app
app.app_context().push()

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='!', case_insensitive=True, intents=intents, help_command=ImperiumHelpCommand())

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
async def on_reaction_add(reaction, user):
  # ignore own reactions
  if user == bot.user:
    return
  # wastebasket handling if the wastbasked was created by bot
  users = await reaction.users().flatten()
  if reaction.emoji == wastebasket_emoji and bot.user in users:
    await reaction.message.delete()

@bot.event
async def on_ready():
    """loads custom emojis upon ready"""
    logger.info('Logged in as')
    logger.info(bot.user.name)
    logger.info(bot.user.id)
    logger.info('------')
    # rewrite default discord emojis with the server supported ones
    for emoji in bot.emojis:
        PackHelper.emojis[emoji.name] = str(emoji)

    act = discord.Game(f"Imperium Season {current_season()}")
    await bot.change_presence(status=discord.Status.online, activity=act)

cogs_dir = os.path.join(ROOT, 'bot/cogs')
# Here we load our extensions(cogs) that are located in the cogs directory. Any file in here attempts to load.
if __name__ == '__main__':
    for extension in [f.replace('.py', '') for f in os.listdir(cogs_dir) if os.path.isfile(os.path.join(cogs_dir, f))]:
        try:
            logger.info(f'Loading cog {extension}')
            bot.load_extension("bot.cogs." + extension)
        except (discord.ClientException, ModuleNotFoundError):
            logger.error(f'Failed to load extension {extension}.')

with open(os.path.join(ROOT, 'config/TOKEN'), 'r') as token_file:
    TOKEN = token_file.read()
    
bot.run(TOKEN, bot=True, reconnect=True)

