import discord
import inspect

from discord.ext import commands
from bot.helpers import transform_message
from bot.actions import common

async def send_embed(data, ctx):
    embed = discord.Embed(title=data['embed_title'], description=data['embed_desc'], color=0xEE8700)
    embed.set_thumbnail(url=data['thumbnail_url'])
    for field in data['embed_fields']:
        embed.add_field(name=field['name'], value=transform_message(field['value'], ctx), inline=field['inline'])
    await ctx.send(embed=embed)

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