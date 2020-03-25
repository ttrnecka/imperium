import discord
import inspect

from discord.ext import commands
from bot.helpers import send_embed
from bot.actions import common

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

def setup(bot):
    bot.add_cog(Common(bot))