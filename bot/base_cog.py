import traceback

from discord.ext import commands
from bot.helpers import logger
from models.data_models import db

class ImperiumCog(commands.Cog):
  async def cog_command_error(self, ctx, error):
      await ctx.send(error)
      text = type(error).__name__ +": "+str(error)
      logger.error(text)
      logger.error(traceback.format_exc())
      await ctx.send_help(ctx.command)
      await self.cog_after_invoke(ctx)

  async def cog_after_invoke(self, ctx):
    db.session.remove()