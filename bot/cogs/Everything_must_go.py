import discord
from .. import dice
from discord.ext import commands
from discord.utils import get


class EverythingMustGo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command()
    async def EverythingMustGo(self, ctx, *, member: discord.Member = None):
        """Roll a D6. Each team in the tournament must apply that many -AV injuries to their own team. 
        Each coach may choose which of their own players will be affected, but no player may take more 
        than one -AV injury as a result of this card."""
        
        result = dice.dice(6,1)
        embed = discord.Embed(title='Everything must go!', color=0xEE8700)
        embed.set_thumbnail(url='https://cdn2.rebbl.net/images/skills/ArmourBust.png')
        description = f'Each team in the tournament must apply **{result[0]} -AV injuries** to their team.\nEach coach may choose which of their own team players will be affected. No player may take more than one -AV injury as a result of this card.'
        embed.add_field(name=':game_die: :' + ','.join(map(str,result)), value=description, inline=False)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(EverythingMustGo(bot))  