import discord
import inspect
import traceback

from discord.ext import commands
from bot.helpers import send_embed, logger
from bot.actions import common
from models.data_models import db, Coach
from services import CoachService

RULES_LINK = "https://bit.ly/2P9Y07F"

class Common(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command()
    async def injury(self, ctx):
        """Roll a D8 to see what inujury to apply"""

        # calls the same named method from special_play
        data = getattr(common, inspect.currentframe().f_code.co_name)()
        await send_embed(data, ctx)

    @commands.command()
    async def newcoach(self, ctx):
      """Creates new coach account"""
      coach = CoachService.discord_user_to_coach(ctx.author)
      if coach:
        await ctx.send(f"**{ctx.author.mention}** account exists already")
      elif Coach.get_by_discord_id(ctx.author.id, deleted=True):
        await ctx.send(f"**{ctx.author.mention}** account is inactive, use the web page to activate it")
      else:
        coach = CoachService.new_coach(ctx.author, ctx.author.id)
        msg = f"**{ctx.author.mention}** account created\n" \
            + f"**Bank:** {coach.account.amount} coins\n" \
            + f"**Rules**: <{RULES_LINK}>"
        await ctx.send(msg)

    async def cog_command_error(self, ctx, error):
      await ctx.send(error)
      text = type(error).__name__ +": "+str(error)
      logger.error(text)
      logger.error(traceback.format_exc())

      await self.cog_after_invoke(ctx)

    async def cog_after_invoke(self, ctx):
      db.session.remove()

def setup(bot):
    bot.add_cog(Common(bot))